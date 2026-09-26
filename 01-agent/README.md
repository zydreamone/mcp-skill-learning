# 01 Agent

状态：**Completed**。七个小实验已完成；下一阶段是 [02 Tool Calling](../02-tool-calling/README.md)。本阶段只学习 Agent 的决策与执行循环，没有实现工具调用。

## 学习目标

理解普通 LLM 单次生成与 Agent 持续执行任务的区别；认识 Agent Loop，以及 Goal、State、Context、History、Action、Observation、Action Space 的关系。逐步把规则决策替换为 LLM 决策，并理解 Parser、Validator、Runtime 如何处理真实模型的失败与恢复。

## Experiment 01 - Rule-Based Agent Loop

[代码](examples/01_rule_based_agent.py)：从 0 开始每轮加 1，达到 3 后结束。用一个固定动作看清 Goal、State、Action、Observation、Loop、Termination。

## Experiment 02 - Multi-Action Agent

[代码](examples/02_multi_action_agent.py)：从固定加 1 扩展到 `increment`、`decrement`、`double`、`stop`。根据当前 State 从 Action Space 选择动作，理解 Decision；默认路径为 `1 → 2 → 4 → 5 → 6 → stop`。

## Experiment 03 - Agent History

[代码](examples/03_agent_history.py)：每轮记录 `State Before`、Action、Observation，形成 Execution Trace。使用状态副本保留当时的值，区别当前 State 与过去的 History。

## Experiment 04 - Context-Aware Agent

[代码](examples/04_context_aware_agent.py)：Decision 读取 Goal、State、History、Rules 和 Available Actions。`double` 最多使用一次，因此历史开始影响下一步动作。

## Experiment 05 - Fake LLM Decision

[代码](examples/05_fake_llm_decision.py)：模拟 LLM 在 Decision 中的位置；Fake LLM 内部仍用 Python 规则。

```text
Context → Prompt → Fake LLM → Text Response → parse_action → Action
```

由此学习 Prompt、LLM Response、Action Parsing 和 Output Validation；`execute()` 负责真正执行。

## Experiment 06 - Real LLM Decision

[代码](examples/06_real_llm_decision.py)：通过本地 Ollama + `qwen3:8b` 接入真实模型，替换实验 05 的 Fake LLM。

```text
Context → Prompt → Ollama API → qwen3:8b → LLM Response
        → parse_action → validate_action → execute → Observation
```

LLM 负责提出 Decision；Runtime 负责解析、校验、执行、记录历史、更新状态及限制最大步数。真实运行到达目标 6；一次早期运行中，模型第二次建议 `double` 被校验拒绝，调整 Prompt 后完成任务。

## Experiment 07 - LLM Failure & Recovery

[代码](examples/07_llm_failure_recovery.py)：当请求、解析或校验失败时，拒绝该建议，附带失败原因重新请求模型。Parsing Failure、Validation Failure、Retry、Feedback、Decision Attempt、Execution History、`MAX_RETRIES` 和 `MAX_STEPS` 是本实验的核心。

默认演示模式在第 2 步首次尝试**人为注入**违规输出；真实模型的响应和注入值分别显示。失败尝试只进入 Decision Attempts，成功执行的动作才进入 Execution History。实测 6 个 Step、7 次尝试、1 次 Retry 后完成；未触发两个上限。

## 当前阶段成果

目前已具备基础 Agent 的 Goal、State、Context、History、Action Space、Decision、LLM Decision、Parser、Validator、Executor、Retry、Feedback 与 Runtime Protection。七个实验分别展示从简单规则到本地模型、再到失败恢复的演进。实现仍是教学用的数字任务，尚无真实工具能力。

在仓库根目录按需运行单个实验：

```powershell
python 01-agent/examples/01_rule_based_agent.py
python 01-agent/examples/02_multi_action_agent.py
python 01-agent/examples/03_agent_history.py
python 01-agent/examples/04_context_aware_agent.py
python 01-agent/examples/05_fake_llm_decision.py
python -X utf8 01-agent/examples/06_real_llm_decision.py
python -X utf8 01-agent/examples/07_llm_failure_recovery.py
```

均不需要第三方 Python 依赖。实验 06、07 需要运行中的本地 Ollama 服务及已下载的 `qwen3:8b`；实验 07 的故障注入可在其文件中设 `FORCE_FAILURE_DEMO=False` 关闭。复习概念见 [Agent 基础笔记](notes/agent-basics.md)，长期背景见 [AI_LOG](../AI_LOG.md)。

## 下一阶段

进入 [02-tool-calling](../02-tool-calling/README.md)。本阶段回答“Agent 应该做什么”；下一阶段学习“Agent 如何调用真实工具完成动作”，从读取文件、搜索文本和函数调用等最小工具开始。该阶段尚未完成。
