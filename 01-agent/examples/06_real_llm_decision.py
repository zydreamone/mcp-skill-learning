"""实验 06：真正通过 Ollama 调用 qwen3:8b，让模型负责 Decision。

Context → Prompt → Ollama API → LLM Response → Parse Action → execute
与实验 05 相比，去掉 Fake LLM 的 Python 决策规则，改为真实 HTTP 请求。
只使用标准库；不依赖 OLLAMA_LOCAL 项目的文件，也不使用 Agent 框架。
"""

import json
import re
import sys
from urllib import error, request

ACTIONS = ["increment", "decrement", "double", "stop"]
MODEL = "qwen3:8b"
API_URL = "http://localhost:11434/api/generate"
TIMEOUT_SECONDS = 120
MAX_STEPS = 10  # 包含最后一次 stop，最多调用模型 10 轮。


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


def decide(context):
    # 只组织调用流程，不包含替模型选择动作的 Python 规则，也不设回退答案。
    prompt = build_prompt(context)
    print("Prompt:")
    print(prompt)
    llm_response = call_llm(prompt)
    print("Real LLM Response:")
    print(llm_response)
    action = parse_action(llm_response, context["available_actions"])
    print(f"Parsed Action: {action}")
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
    history = []
    step = 0
    while not state["finished"]:
        # 在下一次模型调用之前检查，避免调用第 MAX_STEPS+1 轮。
        if step >= MAX_STEPS:
            raise RuntimeError(f"达到 MAX_STEPS={MAX_STEPS}，任务未完成；current={state['current']}")
        step += 1
        observation = observe(state)
        context = build_context(state, history)
        print(f"=== Step {step} ===")
        print("Context Summary:")
        print(f"current={observation['current']}, target={observation['target']}")
        print(f"double_used={count_action_usage(history, 'double')}/{context['rules']['max_double_uses']}")

        action = decide(context)
        validate_action(action, context)
        observation = execute(action, state)
        print(f"Observation: current={observation['current']}, finished={observation['finished']}")
        record_history(history, step, state, action, observation)
        update_state(state, observation)
        print()

    print("Task completed.")
    print(f"Total steps: {step}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError) as exc:
        # 明确显示失败并返回非零退出码，不把错误伪装成任务完成。
        print(f"Task failed: {exc}", file=sys.stderr)
        sys.exit(1)
