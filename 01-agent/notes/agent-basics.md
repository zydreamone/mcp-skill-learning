# Agent 基础复习笔记

阶段 01 已完成实验 01–07。这份笔记按概念演进整理；实验实现和运行方式见 [阶段总览](../README.md)。

## 1. LLM 与 Agent

LLM 根据输入生成内容，本身不会持续执行任务。Agent 在 Goal 下运行循环：观察当前状态、决定 Action、执行、读取 Observation，再进入下一轮。实验 01–04 使用 Python 规则，实验 05 模拟模型位置，实验 06–07 才真实调用本地模型。

## 2. Goal、State、Context、History

- **Goal**：希望达成的结果。实验 01 从 0 到 3，实验 02–07 从 1 到 6。
- **State**：任务现在是什么样；示例字典含 `current`、`target`、`finished`。执行结果由 `update_state()` 写入。
- **History**：过去发生过什么。实验 03 开始保存逐步记录；实验 04 开始用历史统计 double 使用次数。
- **State Before**：本轮动作执行前的状态快照。实验 03 在更新 State 之前用 `state.copy()` 保存；只有整数、布尔值时浅拷贝足够，嵌套可变值要重新考虑复制方式。
- **Context**：决策时可使用的相关信息集合，可含 Goal、Current State、History、Rules、Available Actions。实验 04 的 `build_context()` 显式构造字典。State 是“现在”，History 是“过去”，两者都能成为 Context 的一部分。

## 3. Action、Observation 与循环

- **Action**：本轮选择做什么。实验 01 运行时只有加 1；实验 02 扩展为 `increment`、`decrement`、`double`、`stop`。
- **Action Space**：全部候选动作，在代码中由 `ACTIONS` 表示；候选动作还需满足当前 Rules。实验 02 默认路径不会使用 decrement，但 `current=7,target=6` 时会选它。
- **Decision**：从 Context 选择下一步动作。实验 02 基于 State，实验 04 结合 History 和 double 最多一次的规则。
- **Observation**：观察或执行动作后得到的信息，例如 double 后 `current=2`；执行函数先返回结果，不直接改变 State。
- **Agent Loop**：`while` 重复“观察 → 决策 → 执行 → 记录 → 更新 → 下一轮”。不同实验逐步加入 Context、Parser、Validator 和 Retry。
- **Termination**：循环结束条件。实验 01 达到 3 就设置 `finished=True`；实验 02–07 到达 6 后还执行一次 stop，随后结束。

实验 01 的路径是 `0 → 1 → 2 → 3`，共 3 步。实验 02 的路径是 `1 → 2 → 4 → 5 → 6 → stop`，共 5 轮。实验 03 沿用实验 02 的路径，额外保存 5 条 Execution Trace。实验 04 限制 double 一次，路径改为 `1 → 2 → 3 → 4 → 5 → 6 → stop`，共 6 轮。

## 4. Prompt 与 LLM Decision

- **Prompt**：`build_prompt()` 把 Goal、State、Rules、History、Available Actions 和输出要求整理成模型可读的文本。模型不能直接读取 Python 字典。
- **Fake LLM**：实验 05 的 `fake_llm(prompt, context)` 为稳定演示直接读取 Context 并执行 Python 规则，返回文本，例如 `double`；它不理解 Prompt，也不是真实模型。
- **Real LLM**：实验 06、07 把 Prompt 发送给本地 `qwen3:8b`，由模型返回建议文本。其输出可能变化，因此不能保证每次都遵守指令。
- **Ollama**：本地模型运行服务。代码经 `POST http://localhost:11434/api/generate` 发送非流式请求，读取 JSON 的 `response` 字段；使用 Python 标准库，无第三方 Agent 框架。
- **LLM Response**：尚未执行的模型文本。实验 05 用 Fake LLM 产生，实验 06–07 用真实模型产生；请求失败或空内容都要明确报错。

实验 04 是 `Context → Python Rules → Action`；实验 05 是 `Context → Prompt → Fake LLM → Text Response → Action`；实验 06 将中间部分替换为 `Ollama API → qwen3:8b`。实验 05、06 都需解析文本后才能执行。

## 5. Parser、Validator、Executor

- **parse_action()**（Parser）：做格式校验。实验 05 去除首尾空白并转小写；实验 06、07 还允许简单引号或 Markdown 包裹。最终完整内容必须是**一个**合法动作。`jump`、`double or increment` 和解释性句子不能靠猜测接受。
- **validate_action()**（Validator）：做业务规则校验。`double` 虽是合法文本，但第二次使用会超限；未达目标时 stop 也不合法。检查失败要拒绝，不能偷偷改成其他动作。
- **execute()**（Executor）：真正执行动作并返回 Observation；LLM 负责提出 Decision，不能直接修改 State。实验 06、07 的 execute 也拒绝未知动作和提前 stop。
- **Output Validation**：先由 Parser 检查响应格式，再由 Validator 检查任务约束。合法文本不一定是合法行为。

实验 06 首次真实运行时，模型在第 2 轮再次建议 double，被 Validator 拒绝。明确展示剩余次数和判断顺序后，再次运行得到 `double → increment → increment → increment → increment → stop`，到达 6；未关闭校验或让 Python 代选动作。

## 6. History、Failure 与 Recovery

- **Execution History**：只保存实际执行成功的动作，记录 `step`、`state_before`、`action`、`observation`；实验 03 完成后第一条仍是动作前 `current=1` 和动作后 `current=2`。失败建议不能进入此列表，也不能计入 double 已用次数。
- **Decision Attempts**：实验 07 按 Step 保存每次模型尝试，含原始响应、待验证响应、是否注入、解析动作、失败原因与阶段。它与 Execution History 是两类记录。
- **Parsing Failure**：文本无法解析成单个合法动作，例如 jump、多动作或解释句。
- **Validation Failure**：动作名合法，但违反 double 次数或停止条件。
- **Retry**：失败后在**当前 Step 内**重新请求模型。实验 07 的 `MAX_RETRIES=2` 表示首次调用加最多 2 次重试，总共最多 3 次；仍失败则终止。
- **Feedback**：把上次响应、失败阶段和原因加入新 Prompt，提醒模型没有执行该动作、State 未改变。
- **MAX_STEPS**：实验 06、07 最多运行 10 个 Agent Step，防止合法但不前进的动作造成无限循环；Retry 不算新 Step。单次 HTTP 请求另设 120 秒超时。
- **Runtime**：负责循环、请求、解析、校验、执行、重试、步数限制、历史与状态管理。模型只给建议，Runtime 才控制是否执行。

实验 07 默认 `FORCE_FAILURE_DEMO=True`。Step 2 / Attempt 1 的真实模型输出是 `increment`，测试模式**人为替换**为 `double`；Parser 接受名称，Validator 拒绝超次数。Attempt 2 附带 Feedback 再次真实调用，返回 `increment` 并执行。最终 6 个 Step、7 次 Decision Attempt、1 次 Retry、6 条 Execution History，到达 6；未触发 MAX_RETRIES 或 MAX_STEPS。这次失败是教学注入，不是模型真实错误。若第一步未用 double，注入值改为 jump，以确保演示解析失败。关闭开关可观察无注入的模型行为。

## 7. 当前阶段完整 Agent 架构

```text
User Goal
   ↓
Context
  ├─ State（现在）
  ├─ History（过去）
  ├─ Rules
  └─ Available Actions
   ↓
Prompt → Ollama → LLM → LLM Response
   ↓
Parser（格式）
   ↓
Validator（业务规则）
  ├─ Failed → Decision Attempt → Feedback → Retry（同一步，次数受限）
  └─ Passed
       ↓
Executor → Observation
       ↓
Record Execution History（保存 State Before）
       ↓
Update State
       ↓
Next Step（受 MAX_STEPS 限制）
```

图中先记录执行历史、再更新 State，与实验 03–07 的代码顺序一致，确保 `state_before` 是动作前的副本。下一阶段 [02 Tool Calling](../../02-tool-calling/README.md) 学习让动作连接到读取文件、搜索文本等真实工具；本阶段尚未实现这些工具。
