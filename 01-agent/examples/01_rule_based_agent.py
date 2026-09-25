"""实验 01：用规则驱动 Agent，从 0 开始每轮加 1，直到达到 3。"""


def observe(state):
    # Observation（观察）：读取当前能看到的信息，返回一个新的字典。
    return {"current": state["current"], "target": state["target"]}


def decide(state):
    # Action（动作）：根据简单规则做决定，这里没有调用任何模型。
    if state["current"] < state["target"]:
        return "increment"
    return "stop"


def execute(action, state):
    # 执行动作，返回结果作为 Observation，暂时不修改 State。
    if action == "increment":
        return {"current": state["current"] + 1}
    return {"current": state["current"]}


def update_state(state, observation):
    # State（状态）：把动作的结果记下来，供下一轮决策使用。
    state["current"] = observation["current"]
    # Termination（终止条件）：达到目标就标记为完成。
    state["finished"] = state["current"] >= state["target"]


def main():
    # Goal（目标）：让 current 达到 target，也就是数字 3。
    # State 保存当前数字、目标数字，以及任务是否完成。
    state = {"current": 0, "target": 3, "finished": False}
    step = 0

    # Agent Loop：观察 → 决策 → 执行 → 更新状态 → 检查是否继续。
    while not state["finished"]:
        step += 1
        print(f"=== Step {step} ===")

        observation = observe(state)
        print(f"State: current={observation['current']}, target={observation['target']}")

        action = decide(state)
        print(f"Action: {action}")

        observation = execute(action, state)
        print(f"Observation: current={observation['current']}")

        update_state(state, observation)
        print()

    print("Task completed.")


# 直接运行这个文件时，从 main 函数开始执行。
if __name__ == "__main__":
    main()
