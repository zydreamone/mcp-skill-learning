# 阶段 1：Agent

- **阶段目标**：理解 Agent 与普通 LLM 的区别，以及 Agent Loop、State、Context、Action、Observation。
- **计划实验**：画出执行循环，用最小 Python 示例观察行动、反馈与状态更新，并设置停止条件。
- **预计产物**：`examples/` 中的最小循环示例和流程笔记。

状态：已完成实验 01–03，继续学习中；详见 [总路线](../LEARNING_ROADMAP.md)。

## Experiment 01: Rule-Based Agent Loop

[实验代码](examples/01_rule_based_agent.py)：从 0 开始，每轮加 1，直到达到 3。解决“最小 Agent Loop 如何运行”的问题，观察决策、执行、状态更新与终止的关系。

## Experiment 02: Multi-Action Agent

[实验代码](examples/02_multi_action_agent.py)：从 1 开始，根据当前状态选择 `increment`、`decrement`、`double` 或 `stop`，达到 6 后停止。解决“如何从 Action Space 中选择下一步动作”的问题。

## Experiment 03: Agent History / Execution Trace

[实验代码](examples/03_agent_history.py)：沿用实验 02 的任务，在更新 State 前记录每一步的状态副本、动作和观察结果，结束后展示执行轨迹。解决“如何保留过去的执行过程，而不只看到当前状态”的问题。

在项目根目录运行：

```powershell
python 01-agent/examples/01_rule_based_agent.py
python 01-agent/examples/02_multi_action_agent.py
python 01-agent/examples/03_agent_history.py
```

三个实验均仅使用 Python 基础语法，无需安装依赖。

学习记录见 [Agent 基础笔记](notes/agent-basics.md)，后续继续补充观察与问题。
