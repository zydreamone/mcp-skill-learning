"""实验 03：保留当前状态，同时记录 Agent 每一步的执行历史。"""

# Action Space：Agent 可以选择的全部动作，规则沿用实验 02。
ACTIONS = ["increment", "decrement", "double", "stop"]


def observe(state):
    # 读取当前可观察的信息，不修改 State。
    return {"current": state["current"], "target": state["target"]}


def decide(state):
    current = state["current"]
    target = state["target"]

    if current == target:
        return "stop"
    if 0 < current and current * 2 <= target:
        return "double"
    if current < target:
        return "increment"
    return "decrement"


def execute(action, state):
    # 先计算执行结果，State 统一交给 update_state 更新。
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
    state["current"] = observation["current"]
    state["finished"] = observation["finished"]


def record_history(history, step, state, action, observation):
    # 必须在更新 State 前记录：copy() 保存当时状态的独立字典。
    # 若直接保存 state，后续更新会让历史记录也指向最新状态。
    # 这里的值只有整数和布尔值，浅拷贝就够用。
    history.append({
        "step": step,
        "state_before": state.copy(),
        "action": action,
        "observation": observation.copy(),
    })


def print_history(history):
    # Execution Trace：按发生顺序展示记录，方便回顾每步做了什么。
    print("=== Execution History ===")
    for record in history:
        state_before = record["state_before"]
        observation = record["observation"]
        print(f"Step {record['step']}:")
        print(f"State Before: current={state_before['current']}, target={state_before['target']}")
        print(f"Action: {record['action']}")
        print(f"Observation: current={observation['current']}, finished={observation['finished']}")
        print()


def main():
    # Goal：从 1 到达 6，再选择 stop。
    # State 是“现在”：当前时刻任务处于什么状态。
    state = {"current": 1, "target": 6, "finished": False}
    # History 是“过去”：之前每一步发生过什么。
    history = []
    step = 0

    # 真实 Agent 往往结合 Goal、Context、Current State、History 决策。
    # 本实验只记录和展示 History，decide 仍仅根据当前 State 选择动作。
    # Loop：观察 → 决策 → 执行 → 记录 History → 更新 State → 下一轮。
    while not state["finished"]:
        step += 1
        print(f"=== Step {step} ===")

        observation = observe(state)
        print(f"State: current={observation['current']}, target={observation['target']}")
        print(f"Available Actions: {', '.join(ACTIONS)}")

        action = decide(state)
        print(f"Selected Action: {action}")

        observation = execute(action, state)
        print(f"Observation: current={observation['current']}, finished={observation['finished']}")

        record_history(history, step, state, action, observation)
        update_state(state, observation)
        print()

    print("Task completed.")
    print()
    print_history(history)


if __name__ == "__main__":
    main()
