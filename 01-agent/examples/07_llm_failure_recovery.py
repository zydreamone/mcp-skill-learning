"""实验 07：LLM Failure & Recovery，失败时拒绝并带反馈重新请求模型。

LLM 是概率性的，即使低温度也可能不遵守要求。
Parser 校验格式，Validator 校验业务规则；合法文本不代表合法行为。
Retry 尝试恢复，Feedback 帮助模型修正；Runtime 保护循环与执行边界。
模型只能给建议，不能直接执行动作或修改 State。
"""

import json
import re
import sys
from urllib import error, request

ACTIONS = ["increment", "decrement", "double", "stop"]
MODEL = "qwen3:8b"
API_URL = "http://localhost:11434/api/generate"
TIMEOUT_SECONDS = 120
MAX_STEPS = 10  # 最多 10 个 Agent Step，重试不增加 Step。
MAX_RETRIES = 2  # 每一步：首次调用 + 最多 2 次重试，共最多 3 次调用。
FORCE_FAILURE_DEMO = True  # 教学用人为故障，不代表真实模型犯错。
FAILURE_DEMO_STEP = 2


def observe(state):
    # 读取当前状态，不改变原来的字典。
    return {"current": state["current"], "target": state["target"]}


def build_context(state, history):
    # Context 汇集本轮决策所需的信息；State 是现在，History 是过去。
    return {
        "goal": {"description": "让 current 到达 target", "target": state["target"]},
        "state": state,
        "history": history,
        "rules": {"max_double_uses": 1},
        "available_actions": ACTIONS,
    }


def count_action_usage(history, action):
    count = 0
    for record in history:
        if record["action"] == action:
            count += 1
    return count


def build_prompt(context):
    # 把 Python 数据变成普通文本；真实模型只能看到请求中发送的内容。
    state = context["state"]
    double_used = count_action_usage(context["history"], "double")
    history_lines = []
    for record in context["history"]:
        history_lines.append(
            f"Step {record['step']}: action={record['action']}, "
            f"result={record['observation']['current']}"
        )
    history_text = "; ".join(history_lines) if history_lines else "无"
    return "\n".join([
        "你是一个 Agent 的决策模块。请根据以下信息选择下一步动作。",
        f"Goal: 让 current 到达 {context['goal']['target']}",
        f"Current State: current={state['current']}, target={state['target']}, finished={state['finished']}",
        f"Rules: double 最多使用 {context['rules']['max_double_uses']} 次，已使用 {double_used} 次。",
        "动作含义：increment 加1；decrement 减1；double 乘2；stop 停止。",
        f"double 剩余次数：{context['rules']['max_double_uses'] - double_used}。剩余为0时绝对禁止 double，即使翻倍不超过目标。",
        "请按顺序判断，命中一条就结束：",
        "1. current == target：选择 stop。",
        "2. current > target：选择 decrement。",
        "3. current < target 且 double 剩余次数为0：只能选择 increment。",
        "4. current < target 且 double 剩余次数大于0，且 0 < current、current * 2 <= target：选择 double。",
        "5. 其余 current < target 的情况：选择 increment。未到目标禁止 stop。",
        f"History: {history_text}",
        f"Available Actions: {', '.join(context['available_actions'])}",
        "严格要求：只返回一个动作名称；不要解释、Markdown、标点或任何额外文字。",
    ])


def call_llm(prompt):
    # LLM 只接收 Prompt 并返回文本，不能直接访问或修改本程序的 State。
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,  # 一次接收完整 JSON，不处理流式分块。
        "think": False,  # Qwen3 关闭思考输出，适合短动作决策。
        "options": {"temperature": 0, "num_ctx": 4096, "num_predict": 128},
    }
    req = request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    # localhost 请求不经过系统代理；只影响此客户端，不修改系统设置。
    client = request.build_opener(request.ProxyHandler({}))
    try:
        with client.open(req, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200:
                raise RuntimeError(f"Ollama HTTP 状态异常：{response.status}")
            result = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama HTTP {exc.code}：{detail}；请检查模型与 API") from exc
    except error.URLError as exc:
        # urllib 的连接超时也可能包装在 URLError.reason 中。
        if isinstance(exc.reason, TimeoutError):
            raise RuntimeError(f"Ollama 请求超时（{TIMEOUT_SECONDS} 秒）") from exc
        raise RuntimeError(f"无法连接 Ollama：{exc.reason}；请检查服务 {API_URL}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"Ollama 请求超时（{TIMEOUT_SECONDS} 秒）") from exc
    except (ValueError, UnicodeError) as exc:
        raise RuntimeError("Ollama 响应不是有效的 UTF-8 JSON") from exc

    if not isinstance(result, dict):
        raise RuntimeError("Ollama JSON 格式异常：预期对象")
    if result.get("error"):
        raise RuntimeError(f"Ollama 返回错误：{result['error']}")
    if "response" not in result:
        raise RuntimeError("Ollama JSON 缺少 response 字段")
    text = result["response"]
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("Ollama response 不是文本或返回内容为空")
    if result.get("done_reason") == "length":
        raise RuntimeError("模型输出达到长度上限，拒绝使用可能被截断的动作")
    return text  # 保留原始文本，交给 parse_action 统一处理。


def parse_action(llm_response, available_actions):
    # 采用严格方案：只接受整个响应是一个动作，不从解释性句子中猜答案。
    if not isinstance(llm_response, str):
        raise ValueError("LLM 响应必须是字符串")
    action = llm_response.strip().lower()
    # 接受简单代码块，例如 ```\ndouble\n``` 或 ```text\ndouble\n```。
    block = re.fullmatch(r"```(?:text|plaintext)?\s*\n(.*?)\n```", action, re.DOTALL)
    if block:
        action = block.group(1).strip()
    else:
        # 只去除一层成对包裹，支持 `double`、**double**、*double* 和引号。
        for wrapper in ("**", "`", "*", '"', "'"):
            if action.startswith(wrapper) and action.endswith(wrapper):
                action = action[len(wrapper):-len(wrapper)].strip()
                break
    if action not in available_actions:
        raise ValueError(f"非法 LLM 输出，无法唯一确定动作：{llm_response!r}")
    return action


def decide_with_retry(context):
    # 每轮独立保存 Decision Attempts，失败建议不能写入 Execution History。
    attempts = context["decision_attempts"]
    feedback = ""
    for attempt in range(1, MAX_RETRIES + 2):
        print(f"Attempt {attempt}")
        prompt = build_prompt(context)
        if feedback:
            prompt += "\n\nPrevious attempt failed:\n" + feedback
            print("Retry Feedback:")
            print(feedback)

        record = {
            "attempt": attempt,
            "real_response": None,
            "response": None,
            "injected": False,
            "action": None,
            "passed": False,
            "error": None,
            "stage": "Request",
        }
        try:
            # 每次 attempt 都真正调用 Ollama，包括故障注入的那一次。
            raw = call_llm(prompt)
            record["real_response"] = raw
            print("Real LLM Response:")
            print(raw)
            response = raw
            if FORCE_FAILURE_DEMO and context["step"] == FAILURE_DEMO_STEP and attempt == 1:
                # 人为制造失败：只替换指定 step 的第一次响应用于教学。
                # 默认轨迹已用过 double；若模型先选了 increment，则用 jump
                # 确保演示一次解析失败，而不把未违规的 double 误报为失败。
                response = "double" if count_action_usage(context["history"], "double") else "jump"
                record["injected"] = True
                print(f"[DEMO] Injected Response: {response} (人为故障，不是模型真实输出)")
            record["response"] = response

            record["stage"] = "Parsing"
            action = parse_action(response, context["available_actions"])
            record["action"] = action
            print(f"Parsed Action: {action}")
            record["stage"] = "Validation"
            validate_action(action, context)
        except (ValueError, RuntimeError, OSError) as exc:
            # 请求、解析或校验失败都不能进入 execute；保留原因后再请求。
            record["error"] = str(exc)
            attempts.append(record)
            print(f"{record['stage']} Failed: {exc}")
            failed_output = repr(record["response"]) if record["response"] is not None else "未取得响应"
            source_note = "（该响应为教学测试注入）" if record["injected"] else ""
            feedback = (
                f"上一次待验证响应：{failed_output}{source_note}。\n"
                f"失败阶段：{record['stage']}；原因：{exc}。\n"
                "该建议没有执行，State 和 Execution History 未改变。"
                "请根据当前目标、历史及规则重新选择，只返回一个合法动作名称。"
            )
            if attempt == MAX_RETRIES + 1:
                raise RuntimeError(
                    f"Step {context['step']} 耗尽 MAX_RETRIES={MAX_RETRIES}，"
                    f"共尝试 {attempt} 次；最后错误：{exc}"
                ) from exc
            print()
            continue

        record["passed"] = True
        attempts.append(record)
        print("Validation: passed")
        # 不偷偷更换模型动作；只把解析和校验通过的原建议交给调用方。
        return action


def validate_action(action, context):
    # 名称合法不等于行为合规：这里只拒绝违规建议，不替换或生成动作。
    if action not in context["available_actions"]:
        raise ValueError(f"动作不在 Action Space 中：{action}")
    if action == "double":
        used = count_action_usage(context["history"], "double")
        if used >= context["rules"]["max_double_uses"]:
            raise ValueError("LLM 决策违反规则：double 已达到使用上限")
    if action == "stop" and context["state"]["current"] != context["goal"]["target"]:
        raise ValueError("LLM 决策违反规则：尚未达到目标，不能报告完成")


def execute(action, state):
    # LLM 决定“做什么”；本函数才真正计算动作结果，并拒绝未知动作。
    current = state["current"]
    finished = False
    if action == "increment":
        current += 1
    elif action == "decrement":
        current -= 1
    elif action == "double":
        current *= 2
    elif action == "stop":
        if current != state["target"]:
            raise ValueError("未达到目标，不能执行 stop")
        finished = True
    else:
        raise ValueError(f"未知动作：{action}")
    return {"current": current, "finished": finished}


def record_history(history, step, state, action, observation):
    # 只记录已成功执行的动作，更新 State 前保存独立快照。
    history.append({
        "step": step,
        "state_before": state.copy(),
        "action": action,
        "observation": observation.copy(),
    })


def update_state(state, observation):
    state["current"] = observation["current"]
    state["finished"] = observation["finished"]


def main():
    state = {"current": 1, "target": 6, "finished": False}
    history = []  # Execution History：只含实际执行成功的动作。
    decision_attempts = []  # 按 Step 分组的尝试记录，包含失败和成功。
    step = 0
    while not state["finished"]:
        if step >= MAX_STEPS:
            raise RuntimeError(f"达到 MAX_STEPS={MAX_STEPS}，任务未完成；current={state['current']}")
        step += 1
        observation = observe(state)
        context = build_context(state, history)
        context["step"] = step
        context["decision_attempts"] = []
        decision_attempts.append({"step": step, "attempts": context["decision_attempts"]})
        print(f"=== Step {step} ===")
        print(f"State: current={observation['current']}, target={observation['target']}")
        print(f"Double Used: {count_action_usage(history, 'double')}/{context['rules']['max_double_uses']}")

        # 重试全部发生在同一个 Step 内；成功返回后只执行一次动作。
        action = decide_with_retry(context)
        observation = execute(action, state)
        print(f"Observation: current={observation['current']}, finished={observation['finished']}")
        record_history(history, step, state, action, observation)
        update_state(state, observation)
        print()

    total_attempts = sum(len(item["attempts"]) for item in decision_attempts)
    total_retries = total_attempts - step
    print("Task completed.")
    print(f"Total steps: {step}")
    print(f"Decision attempts: {total_attempts}")
    print(f"Total retries: {total_retries}")
    print(f"Execution history entries: {len(history)}")
    # 返回数据便于观察，运行命令行时不影响输出。
    return state, history, decision_attempts


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError) as exc:
        # 明确显示失败并返回非零退出码，不把错误伪装成任务完成。
        print(f"Task failed: {exc}", file=sys.stderr)
        sys.exit(1)
