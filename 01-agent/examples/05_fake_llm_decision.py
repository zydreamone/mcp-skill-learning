"""实验 05：模拟 LLM 在决策阶段的位置，不调用任何真实模型或 API。

实验 04：Context → Python Rules → Action
实验 05：Context → Prompt → Fake LLM → Text Response → Parse Action → Action
本实验内部仍然使用规则，只改变决策流程的结构，不增加模型智能。
"""

# 动作空间：程序支持的全部动作名称，文本响应必须匹配其中一个。
ACTIONS = ["increment", "decrement", "double", "stop"]


def observe(state):
    # 观察当前数字与目标；这里只读取，不修改状态。
    return {"current": state["current"], "target": state["target"]}


def build_context(state, history):
    # Context 汇集当前决策需要的目标、状态、历史、规则和候选动作。
    # state 和 history 是本轮读取的对象；历史里的状态快照另行复制。
    return {
        "goal": {"description": "让 current 到达 target", "target": state["target"]},
        "state": state,
        "history": history,
        "rules": {"max_double_uses": 1},
        "available_actions": ACTIONS,
    }


def count_action_usage(history, action):
    # 统计已经执行的动作，而不是统计模型曾经提出过的建议。
    count = 0
    for record in history:
        if record["action"] == action:
            count += 1
    return count


def build_prompt(context):
    # Prompt 就是普通字符串：把 Context 转换成模型能读取的文本输入。
    # 先把每条历史转换成短句，再用分号连接，便于观察完整执行过程。
    history_lines = []
    for record in context["history"]:
        history_lines.append(
            f"Step {record['step']}: action={record['action']}, "
            f"result={record['observation']['current']}"
        )
    history_text = "; ".join(history_lines) if history_lines else "无"
    state = context["state"]

    # \n 表示换行；join 把多段字符串组合为一个字符串。
    return "\n".join([
        f"Goal: 让 current 到达 {context['goal']['target']}",
        f"Current State: current={state['current']}, target={state['target']}, finished={state['finished']}",
        f"Rules: double 最多使用 {context['rules']['max_double_uses']} 次",
        f"History: {history_text}",
        f"Available Actions: {', '.join(context['available_actions'])}",
        "Question: 请选择下一步 Action，只返回动作名称。",
    ])


def fake_llm(prompt, context):
    # 模拟真实 LLM：返回文本建议，自己不执行动作，也不更新 State。
    # prompt 参数用于展示未来模型接收文本的位置；这里不解析该文本。
    # 为了结果稳定，直接读取 context 并使用实验 04 的规则。
    # 因此修改 Prompt 的措辞不会改变这个 Fake LLM 的判断。
    current = context["state"]["current"]
    target = context["goal"]["target"]
    available_actions = context["available_actions"]
    double_used = count_action_usage(context["history"], "double")

    if current == target:
        if "stop" in available_actions:
            return "stop"
    else:
        if (
            "double" in available_actions
            and double_used < context["rules"]["max_double_uses"]
            and 0 < current
            and current * 2 <= target
        ):
            return "double"
        if current < target and "increment" in available_actions:
            return "increment"
        if current > target and "decrement" in available_actions:
            return "decrement"
    raise ValueError("当前没有符合目标和规则的可用动作")


def parse_action(llm_response, available_actions):
    # 不应无条件相信模型输出：先确认是文本，再规范化并校验。
    if not isinstance(llm_response, str):
        raise ValueError("模型响应必须是字符串")
    # strip 去除首尾空白，lower 转为小写：" Double " → "double"。
    action = llm_response.strip().lower()
    if action not in available_actions:
        # 遇到未知动作直接报错，不猜测、不执行任意文本。
        raise ValueError(f"模型返回了不合法的动作：{llm_response!r}")
    # 这里只验证动作名称，不代表验证了使用次数等所有业务规则。
    return action


def decide(context):
    # 这里不使用 if 规则选动作，只负责连接三个决策阶段。
    # 模型负责“决定做什么”，execute 负责“真正做”。
    prompt = build_prompt(context)
    print("Prompt:")
    print(prompt)

    llm_response = fake_llm(prompt, context)
    print(f"Fake LLM Response: {llm_response}")

    action = parse_action(llm_response, context["available_actions"])
    print(f"Parsed Action: {action}")
    return action


def execute(action, state):
    # 只有到这里才计算动作结果；返回 Observation 供主循环使用。
    current = state["current"]
    finished = False
    if action == "increment":
        current += 1
    elif action == "decrement":
        current -= 1
    elif action == "double":
        current *= 2
    elif action == "stop":
        finished = True
    else:
        raise ValueError(f"未知动作：{action}")
    return {"current": current, "finished": finished}


def record_history(history, step, state, action, observation):
    # 在更新 State 前记录副本，避免过去的记录随当前状态一起改变。
    history.append({
        "step": step,
        "state_before": state.copy(),
        "action": action,
        "observation": observation.copy(),
    })


def update_state(state, observation):
    # State 表示现在：将执行结果写回，下一轮就能观察到新状态。
    state["current"] = observation["current"]
    state["finished"] = observation["finished"]


def main():
    # Goal 是到达 6；History 保存过去的执行记录，开始时为空。
    state = {"current": 1, "target": 6, "finished": False}
    history = []
    step = 0

    # Agent Loop 保持原来的结构，只有 Decision 阶段换成模拟模型流程。
    # 执行 stop 后 finished=True，while 循环结束。
    while not state["finished"]:
        step += 1
        observation = observe(state)
        context = build_context(state, history)
        double_used = count_action_usage(history, "double")

        print(f"=== Step {step} ===")
        print("Context Summary:")
        print(f"current={observation['current']}, target={observation['target']}")
        print(f"double_used={double_used}/{context['rules']['max_double_uses']}")

        action = decide(context)
        observation = execute(action, state)
        print(f"Observation: current={observation['current']}, finished={observation['finished']}")
        record_history(history, step, state, action, observation)
        update_state(state, observation)
        print()

    print("Task completed.")


# 直接运行文件时执行 main；导入文件检查函数时不自动运行整个实验。
if __name__ == "__main__":
    main()
