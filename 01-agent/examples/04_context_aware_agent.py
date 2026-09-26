"""实验 04：结合状态、历史、目标和规则决策，double 最多使用一次。"""

ACTIONS = ["increment", "decrement", "double", "stop"]


def observe(state):
    return {"current": state["current"], "target": state["target"]}


def build_context(state, history):
    # Context：Agent 当前决策时能使用的全部相关信息。
    # State 和 History 都可以是 Context 的一部分。
    # 用字典表达 Goal，把目标数字交给规则判断，不需要理解自然语言。
    return {
        "goal": {"description": "让 current 到达 target", "target": state["target"]},
        "rules": {"max_double_uses": 1},
        "available_actions": ACTIONS,
        "state": state,
        "history": history,
    }


def count_action_usage(history, action):
    # 遍历过去的执行记录，统计指定动作已经执行了几次。
    count = 0
    for record in history:
        if record["action"] == action:
            count += 1
    return count


def decide(context):
    # 决策综合读取 Context，不再只看 current 一个变量。
    goal = context["goal"]
    state = context["state"]
    history = context["history"]
    rules = context["rules"]
    available_actions = context["available_actions"]
    current = state["current"]
    target = goal["target"]
    double_used = count_action_usage(history, "double")

    if current == target:
        if "stop" in available_actions:
            return "stop"
    else:
        if (
            "double" in available_actions
            and double_used < rules["max_double_uses"]
            and 0 < current
            and current * 2 <= target
        ):
            return "double"
        if current < target and "increment" in available_actions:
            return "increment"
        if current > target and "decrement" in available_actions:
            return "decrement"

    # 不选择动作空间之外的动作，也不把无法继续误报为任务完成。
    raise ValueError("当前没有符合目标和规则的可用动作")


def execute(action, state):
    # 返回执行结果，不直接修改 State。
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
    # 在更新状态之前保存副本，让历史保持当时的值。
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
    # State：当前任务“现在是什么样”。History：之前发生过什么。
    state = {"current": 1, "target": 6, "finished": False}
    history = []
    step = 0

    # 真实 Agent 通常根据完整 Context 决策，而不是只看一个变量。
    # 每轮先观察，再构造 Context，决策、执行、记录历史、更新状态。
    while not state["finished"]:
        step += 1
        observation = observe(state)
        context = build_context(state, history)
        double_used = count_action_usage(context["history"], "double")

        print(f"=== Step {step} ===")
        print(f"State: current={observation['current']}, target={observation['target']}")
        # 显示本轮动作执行之前的使用次数。
        print(f"Double Used: {double_used} / {context['rules']['max_double_uses']}")
        print(f"Available Actions: {', '.join(context['available_actions'])}")

        action = decide(context)
        print(f"Selected Action: {action}")
        observation = execute(action, state)
        print(f"Observation: current={observation['current']}, finished={observation['finished']}")

        record_history(history, step, state, action, observation)
        update_state(state, observation)
        print()

    print("Task completed.")


if __name__ == "__main__":
    main()
