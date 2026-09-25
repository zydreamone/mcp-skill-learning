"""实验 02：根据当前状态选择不同动作，从 1 到达 6，再停止。"""

# Action Space（动作空间）是 Agent 可以选择的全部候选动作。
# Agent 不再只执行一个固定动作，而是根据当前 State 决定下一步做什么。
ACTIONS = [
    "increment",
    "decrement",
    "double",
    "stop",
]


def observe(state):
    # 读取当前能观察到的信息，不修改原来的状态。
    return {"current": state["current"], "target": state["target"]}


def decide(state):
    # 按顺序检查规则，返回动作空间中的一个动作。
    current = state["current"]
    target = state["target"]

    if current == target:
        return "stop"
    # 只有翻倍能向上推进、且不超过目标时，才选择 double。
    if 0 < current and current * 2 <= target:
        return "double"
    if current < target:
        return "increment"
    return "decrement"


def execute(action, state):
    # 执行动作，先在局部变量中计算结果，再返回 Observation。
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


def update_state(state, observation):
    # 把执行结果记入 State，供下一轮使用。
    state["current"] = observation["current"]
    state["finished"] = observation["finished"]


def main():
    # Goal：从 1 到达目标数字 6。
    state = {"current": 1, "target": 6, "finished": False}
    step = 0

    # Agent Loop：观察 → 决策 → 执行 → 更新状态。
    # Termination：执行 stop 后，finished 变为 True，循环结束。
    while not state["finished"]:
        step += 1
        print(f"=== Step {step} ===")

        observation = observe(state)
        print("State:")
        print(f"current={observation['current']}")
        print(f"target={observation['target']}")

        print("Available Actions:")
        for available_action in ACTIONS:
            print(available_action)

        action = decide(state)
        print("Selected Action:")
        print(action)

        observation = execute(action, state)
        print("Observation:")
        print(f"current={observation['current']}")
        print(f"finished={observation['finished']}")

        update_state(state, observation)
        print()

    print("Task completed.")


if __name__ == "__main__":
    main()
