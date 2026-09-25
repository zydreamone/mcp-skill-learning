# Agent 基础笔记

基于实验 01–03 记录，后续随学习继续追加。

| 概念 | 简短说明与实验对应 |
| --- | --- |
| Goal（目标） | 希望完成的任务：实验 01 从 0 到 3，实验 02 从 1 到 6。 |
| State（状态） | 程序记住的当前情况；三个实验都用 `state` 字典保存 `current`、`target`、`finished`。 |
| Context（上下文） | 决策时可用的信息；这里包括当前数字、目标和预先写好的规则，没有单独的 Context 对象或模型对话。 |
| Action（动作） | 本轮决定执行的操作；实验 01 运行时一直加 1，实验 02 可以选择翻倍、加 1、减 1 或停止。 |
| Observation（观察） | 读取状态或执行动作后得到的信息；例如翻倍后返回 `current=2`，随后写入 State。 |
| Agent Loop（循环） | `while` 重复执行“观察 → 决策 → 执行 → 更新状态”。 |
| Termination（终止） | 控制循环何时结束；实验 01 达到目标即结束，实验 02 达到目标后再执行一次 `stop`，将 `finished` 设为 `True`。 |
| Action Space（动作空间） | Agent 可选择的全部候选动作；实验 02 的 `ACTIONS` 列表包含 `increment`、`decrement`、`double`、`stop`。 |
| History（历史） | 保存过去发生的事情；实验 03 用 `history` 列表记录每一步的状态副本、动作和观察结果。 |
| Execution Trace（执行轨迹） | 按时间顺序呈现执行过程；实验 03 的 `print_history()` 展示从 1 到 6 再停止的完整轨迹。 |

## 三个实验的区别

- [实验 01](../examples/01_rule_based_agent.py)：理解最小循环，运行路径是 `0 → 1 → 2 → 3`。
- [实验 02](../examples/02_multi_action_agent.py)：理解根据 State 选择 Action，运行路径是 `1 → 2 → 4 → 5 → 6 → stop`，共 5 轮（含停止动作）。
- [实验 03](../examples/03_agent_history.py)：沿用实验 02 的规则和路径，额外记录 5 条历史，完成后回顾执行轨迹。

动作空间不代表每次都要使用所有动作：实验 02 的默认路径没有超过目标，所以不会选择 `decrement`；若当前值为 7、目标为 6，规则就会选择它。

`decide()` 只决定做什么，`execute()` 计算动作结果，`update_state()` 才修改保存的状态。这些都是普通 Python 函数，不涉及 Tool Calling。

这里用规则演示 Agent 的基本流程，并不依赖 LLM，也不追求最少步数。

## State 是现在，History 是过去

实验 03 结束时，当前 State 是 `current=6`、`target=6`、`finished=True`；但第一条 History 仍保存动作前的 `current=1`、动作 `double` 和动作后的 `current=2`。

每条历史包含 `step`、`state_before`、`action`、`observation`。循环顺序为“观察 → 决策 → 执行 → 记录历史 → 更新状态”；`execute()` 不修改 State，所以记录时仍能取得动作前的状态。

`state.copy()` 创建独立字典，避免多条历史共享同一个不断变化的 State。本实验只包含整数和布尔值，浅拷贝足够；以后如果加入嵌套列表或字典，需要重新考虑复制方式。Observation 也保存副本。

真实 Agent 往往结合 Goal、Context、Current State 和 History 决定下一步动作。本实验的 History 仅用于回顾，并未参与 `decide()` 的决策；记录也仅保存在本次运行的内存中。

## 后续补充

继续记录新的实验观察、疑问和对概念的理解。
