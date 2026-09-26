# AI Learning Log

这份文件为未来的 Codex / Agent 保留项目长期上下文、学习记录和关键决策。顶部是当前概览，底部是按“问题--回答”保存的历史；环境与 Git 状态是记录时的快照，接续工作时先实地检查。最后整理日期：2026-09-26。

## Project Identity

| 项目 | 内容 |
| --- | --- |
| Project | MCP / Skill / Agent Learning Project |
| Root | `E:\projects_mcp_skill\MCP_SKILL` |
| GitHub | https://github.com/zydreamone/mcp-skill-learning.git |
| Primary Goal | 通过实操逐步学习 Agent → Tool Calling → Skill → MCP → 综合 Agent |

项目中的 `E:\projects_mcp_skill\MCP_SKILL` 是实际工作目录；用户消息有时写成 `E:\projects\_mcp\_skill\MCP_SKILL`，操作前应以当前仓库根目录为准。独立的 Ollama 测试目录是 `E:\projects_mcp_skill\OLLAMA_LOCAL`，不是本仓库的一部分。

## Learning Method

- 每次只推进一个小实验：先理解概念，再实现、运行、观察并复盘。
- 每次实验同步更新该阶段 README 和 notes；阶段收尾再更新根 README 与路线图。
- 优先使用简单 Python、普通函数与中文注释，理解底层机制；当前没有 LangChain、LangGraph 等大型框架。
- Git commit / push 由用户明确要求时执行；“完成阶段”不等于自动授权推送。

## Environment

| 项目 | 当前记录 |
| --- | --- |
| 系统 / IDE | Windows 11 / VS Code |
| Python | 3.10.11，实验使用标准库，无第三方 Python 依赖 |
| Local LLM | Ollama 0.34.4，模型 `qwen3:8b` |
| Ollama Endpoint | `http://localhost:11434`，生成接口 `/api/generate` |

真实模型实验 06、07 需要 Ollama 服务和本地模型；实验 01–05 不需要。版本和服务状态可能变化，复现前检查。

## Repository Status

| 项目 | 状态 |
| --- | --- |
| Current Stage | `01-agent`，**Completed**（阶段学习内容完成，尚未自动提交） |
| Next Stage | `02-tool-calling`，**Next**（尚未实现） |
| 其他阶段 | 待学习 |
| 当前 HEAD | `e54a99b`；仅代表本地检查时的提交，不代表未提交工作 |

本次阶段收尾前，`FRUITS.md` 有用户自己的未暂存修改；实验 04–07 与本日志尚未跟踪，阶段 README 和笔记也有未提交更改。阶段收尾将只更新文档，不更改实验代码；接续时用 `git status` 重新核实。

## Completed Experiments

| 实验 | 目标与关键概念 | 已验证结果 |
| --- | --- | --- |
| 01 Rule-Based Agent Loop | 认识 Goal、State、Action、Observation、Termination | 从 0 加到 3，3 步完成 |
| 02 Multi-Action Agent | 从 Action Space 中按状态选动作 | 从 1 到 6，含 stop 共 5 步 |
| 03 Agent History | 保存 State Before、Action、Observation | 完整记录 5 条执行历史，状态副本不随之后更新 |
| 04 Context-Aware Agent | 用 Goal、State、History、Rules 决策，double 限一次 | 从 1 到 6，含 stop 共 6 步 |
| 05 Fake LLM Decision | 拆出 Prompt、模拟文本响应、Parser | 规则模拟模型，6 步完成，未接真实 API |
| 06 Real LLM Decision | Ollama `qwen3:8b` 真实决策，Parser + Validator + Executor | 6 步完成；早期违规建议曾被拦截 |
| 07 LLM Failure & Recovery | Reject → Feedback → Retry，隔离两类历史 | 人为注入一次违规建议，1 次 Retry 后完成，共 6 步 |

详情与命令见 [01-agent/README.md](01-agent/README.md)；概念复习见 [agent-basics.md](01-agent/notes/agent-basics.md)。实验 07 的注入响应是教学故障，不能误写为真实模型输出。

## Key Architecture Learned

教学上的简写：`Agent ≈ LLM + Loop + State + Context + History + Actions + Runtime`。实验 01–04 说明决策也可由规则完成，并非每个 Agent 都必须有 LLM。本阶段的真实模型实验由 LLM 提出 Decision；Runtime 控制循环、解析、校验、执行、重试和状态；Tool 将在下一阶段负责连接真实能力，目前尚未实现。

## Important Design Decisions

1. 阶段 01 不使用 LangChain、LangGraph 或其他大型 Agent 框架。
2. 真实模型使用本地 Ollama，目前选定 `qwen3:8b`。
3. LLM 不能直接修改 State，也不能直接执行动作。
4. 模型返回的 Action 先经 Parser 检查名称，再经 Validator 检查业务规则；文本合法不代表行为合规。
5. 只有 `execute()` 真正执行动作，失败建议不执行。
6. Execution History 只记录成功执行的动作；Decision Attempts 另行记录每次模型尝试与失败原因。
7. `MAX_STEPS=10` 限制整个循环；实验 07 的 `MAX_RETRIES=2` 表示每步首次调用外最多再试两次。
8. 失败只能 Reject → Feedback → Retry 或报错，不自动偷偷改成另一动作。
9. 实验 07 的 `FORCE_FAILURE_DEMO=True` 是显式教学开关，真实响应和注入值必须区分。

## Current Agent Architecture

```text
Goal → Context（State + History + Rules + Available Actions）
         ↓
       Prompt → Ollama / qwen3:8b → LLM Response
                                     ↓
                              Parser → Validator
                                         ├─ Failed → Feedback → Retry（次数受限）
                                         └─ Passed
                                             ↓
                              Executor → Observation
                                             ↓
                              Record Execution History（保存 State Before）
                                             ↓
                              Update State → Next Loop（步数受限）
```

图中记录执行历史先于更新 State，与实验 03–07 的代码一致。

## Codex Working Rules

- 每次只推进一个学习实验，不一次生成后续阶段的大量代码。
- 先解释正在学习的机制，再用小例子实践；不跳过基础直接引入大型框架。
- 新实验使用新编号文件；未经明确要求不修改、删除历史实验。
- 每次实验同步当前阶段 README 和 notes；阶段完成后整理根 README、路线图和本日志。
- 代码优先简单、可读、带中文注释；区分真实运行结果与人为注入、模拟测试。
- 默认不执行 git commit 或 push，未经明确要求不更改 Git remote。
- 尊重用户已有文件及未提交更改，尤其不要覆盖 `FRUITS.md`。

## Next Objective

下一阶段：`02-tool-calling`，**尚未开始**。核心问题从“Agent 下一步该做什么”转向“Agent 如何调用真实 Tool 完成动作”，逐步学习函数调用、读取文件、搜索文本和外部能力；先做最小工具实验，不提前实现 MCP 或 Skill。

## Historical Conversation Log

以下保留已有“问题--回答”工作经历。各条记录描述发生时的状态；第 11、17 条是旧快照，不能覆盖上方当前进度。

## 01 项目目标与工作约定

**问题：这个项目用来做什么，后续代理应该遵守哪些约定？** -- **回答：** 本项目用于系统学习 Agent、Tool Calling、Skill、MCP Server、MCP Client 及综合应用，采用理论、最小实验、中文笔记和 Codex 辅助相结合的方式，逐步演进，不一次性实现大型工程。用户 Python 基础较弱，代码优先使用普通函数和清晰的中文注释，不提前引入复杂框架或未进入阶段的功能。实验 05 特别要求详细中文注释。

实际工作目录为 `E:\projects_mcp_skill\MCP_SKILL`。用户消息中的目录有不同写法，之前均在已确认的当前仓库根目录操作，没有创建额外嵌套目录。远程仓库为 `https://github.com/zydreamone/mcp-skill-learning.git`，不得擅自修改。不要自动提交、推送；只在用户明确要求时执行。新增实验时保留已有实验文件，不覆盖用户自己的笔记。

## 02 初始化学习框架

**问题：搭建清晰、可长期扩展的学习项目，当前只做初始化。** -- **回答：** 已创建根目录 `README.md`、`LEARNING_ROADMAP.md`、`requirements.txt`、`pyproject.toml`、`.gitignore`，建立阶段 00–08 及各阶段 README、`docs/concepts.md`、学习笔记与公共目录、`playground/`。空目录通过 `.gitkeep` 保留。

Python 要求为 `>=3.10`，初始化无第三方依赖。没有提前实现 Agent、Skill 或 MCP，也没有安装 LangChain、LangGraph。阶段路线覆盖 Foundation、Agent、Tool Calling、Skill、MCP Server、MCP Client、综合应用、真实场景和最终 Developer Assistant 项目。初始提交后来由用户完成，提交为 `fbfe8ea chore: initialize MCP and Skill learning repository`。

## 03 修复 Windows Git 安装

**问题：旧 Git 位于 `C:\gittt\Git`，缺少 Bash，导致认证流程失败，如何修复而不破坏项目？** -- **回答：** 检查发现旧版本为 `2.52.0.windows.1`，缺少 `usr\bin\bash.exe`；旧 Credential Manager 可运行。Windows 卸载登记却指向 `E:\comfyui\Git`，对应卸载程序不存在，因此未运行该失效卸载程序，也未直接删除旧目录。

已通过 winget 安装官方 Git for Windows 到 `C:\Program Files\Git`，安装器更新了登记。修复后的命令路径为 `C:\Program Files\Git\cmd\git.exe`，Git 版本 `2.55.0.windows.3`，Bash 版本 `5.3.15`，Credential Manager 版本 `2.9.0`。已调整持久 PATH，让新 Git 优先，移除 `C:\gittt\Git` 的 PATH 条目。当前进程已有管理员权限，没有绕过提权机制。

用户名 `zydreamone`、邮箱 `zydreamone@gmail.com` 原本正确，未重复修改。仓库、首次提交和 origin 保留完整；当时 `git fsck --full` 仅发现无害的悬空空树，没有损坏报告。Credential Manager 的正确版本查询命令为 `git credential-manager --version`。这些版本信息是当时检查结果，后续需要时重新核对。

## 04 排查 Git push 连接超时

**问题：`git push -u origin main` 报 `Failed to connect to github.com:443`，为什么失败？** -- **回答：** 此次错误发生在建立网络连接时，尚未进入认证阶段，与此前缺少 Bash 的安装问题不同。直连 GitHub 曾超时，随后恢复；Windows 当时启用代理 `127.0.0.1:7897`，Git 未配置代理。分别使用直连和临时代理进行只读 `git ls-remote origin` 检查，均成功，因此判断为临时网络连接问题，没有改动持久代理配置。

当时只诊断、未推送，并告知可重试或在同样网络错误出现时使用单次命令代理。代理地址仅是当时环境信息，不应在后续任务中不经检查就写入全局配置。

## 05 实验 01：Rule-Based Agent Loop

**问题：用最简单的规则驱动 Agent，从 0 每轮加 1，直到达到 3。** -- **回答：** 已创建并运行 `01-agent/examples/01_rule_based_agent.py`，采用 `observe()`、`decide()`、`execute()`、`update_state()`、`main()` 和 `while` 循环。运行路径为 `0 → 1 → 2 → 3`，共 3 步，最后输出 `Task completed.`。

State 保存 `current`、`target`、`finished`；Action 是 `increment`；Observation 是执行结果；达到目标后标记完成。使用普通函数和中文注释，没有 class、LLM 或第三方依赖。

## 06 实验 02：Multi-Action Agent

**问题：让 Agent 根据 State 从多个候选动作中选择下一步。** -- **回答：** 已创建并运行 `01-agent/examples/02_multi_action_agent.py`。`ACTIONS` 明确包含 `increment`、`decrement`、`double`、`stop`，初始值 1，目标 6。

实际动作依次为 `double → double → increment → increment → stop`，数字路径为 `1 → 2 → 4 → 5 → 6`，含停止动作共 5 步。默认任务不会使用 decrement；超过目标时会选择它。创建了 `01-agent/notes/agent-basics.md` 并更新阶段 README，记录 Goal、State、Context、Action、Observation、Agent Loop、Termination、Action Space。实验 01 未修改。

## 07 实验 03：Agent History / Execution Trace

**问题：除了当前 State，如何保留每一步发生过的事情？** -- **回答：** 已创建并运行 `01-agent/examples/03_agent_history.py`，沿用实验 02 的任务，增加 `record_history()` 和 `print_history()`。共记录 5 条历史，每条包含 `step`、`state_before`、`action`、`observation`。

循环先执行动作并取得 Observation，再记录历史，最后更新 State。`execute()` 不直接修改 State，因此记录时仍能取得动作前的状态。`state.copy()` 和 `observation.copy()` 保留独立字典；本实验只有整数和布尔值，浅拷贝足够。State 表示现在，History 表示过去。此实验的 History 只用于回顾，没有参与决策。更新阶段 README 和基础笔记，未修改前两个实验及根目录文档。

## 08 提交与推送阶段成果

**问题：把暂存的更改推到仓库。** -- **回答：** 用户明确授权后，检查并提交了暂存的 6 个文件：三个 Agent 实验、阶段 README、基础笔记及用户暂存的 `FRUITS.md`。创建提交 `e54a99b feat: add agent basics experiments and learning notes`，并成功推送到 `origin/main`。当时工作区干净，本地与远程跟踪分支同步。

这次授权已完成，不表示后续实验可以自动提交或推送；后续实验 04、05 均明确要求暂不 commit、push。

## 09 实验 04：Context-Aware Agent

**问题：让决策综合使用 Goal、State、History、Rules、Available Actions，并限制 double 最多一次。** -- **回答：** 已创建并运行 `01-agent/examples/04_context_aware_agent.py`，增加 `build_context()`、`count_action_usage()`，让 `decide(context)` 读取完整上下文。Goal 使用包含说明与目标数字的字典，目标数字来自 State。

实际动作是 `double → increment → increment → increment → increment → stop`，路径为 `1 → 2 → 3 → 4 → 5 → 6`，共 6 步。第二轮虽然翻倍不超过目标，但 History 已记录一次 double，达到 Rules 中的上限，所以选择 increment。候选列表包含某个动作不代表该动作本轮满足约束。更新阶段 README 和基础笔记，前面的实验及根目录文档未修改。

## 10 实验 05：Fake LLM Decision

**问题：模拟未来真实 LLM 在 Decision 阶段的位置，但不调用真实模型。** -- **回答：** 已创建并运行 `01-agent/examples/05_fake_llm_decision.py`，添加详细中文注释，保留实验 04 的任务、状态和 double 次数限制。

架构从实验 04 的 `Context → Python Rules → Action`，改成 `Context → Prompt → Fake LLM → Text Response → Parse Action → Action`。`decide()` 只连接 `build_prompt()`、`fake_llm()`、`parse_action()`，不直接使用 if 规则选择动作。

Prompt 是普通字符串，包含 Goal、Current State、Rules、History、Available Actions 和输出要求。`fake_llm(prompt, context)` 为稳定演示直接读取 Context、使用 Python 规则，不解析 Prompt，也不理解自然语言；返回的是文本建议，真正执行由 `execute()` 完成。

实际运行 6 步，返回文本依次为 `double`、`increment`、`increment`、`increment`、`increment`、`stop`，double 使用一次，最终到达 6 并完成。`parse_action()` 检查字符串类型、去掉首尾空格、转小写、验证动作名称属于候选列表。额外检查通过：`" Double "` 解析为 `"double"`；`"fly"`、空字符串、`"double please"`、`None` 均抛出 `ValueError`。

解析器只验证动作名称，不验证 double 使用次数等业务约束；当前由 Fake LLM 的规则保证次数限制。未来主要替换 `fake_llm()` 的实现即可保留整体循环结构，但真实接入仍需处理失败、循环上限和业务约束。更新阶段 README 与基础笔记，新增 LLM-based Decision、Prompt、LLM Response、Action Parsing、Output Validation 的说明。

## 11 实验 05 完成时的工作状态（历史快照）

**问题：截至本次记录，哪些工作已完成，后续代理应该从哪里继续？** -- **回答：** 已完成阶段 01 的实验 01–05，并分别运行验证。当前只有规则和 Fake LLM，没有真实 LLM、API、Tool Calling、MCP、Skill 或第三方 Agent 框架；未安装依赖。前五个实验仍是独立、可直接运行的 Python 文件。

本次写日志前检查：当前分支为 `main`，本地 HEAD 为 `e54a99b`，本地远程跟踪信息显示与 `origin/main` 一致；此次没有联网核实远程最新状态。阶段 README、基础笔记和用户的 `FRUITS.md` 有未暂存修改，实验 04、05 及本文件 `AI_LOG.md` 尚未跟踪。实验 04、05 没有提交或推送。

运行检查未发现异常，Git 曾提示 LF/CRLF 换行转换。前四个实验、根 `README.md`、`LEARNING_ROADMAP.md` 和 `FRUITS.md` 在实验 05 前后哈希一致。不要把用户自己对 `FRUITS.md` 的修改当作需要撤销或覆盖的内容。

后续先阅读 `01-agent/README.md`、`01-agent/notes/agent-basics.md` 和本日志，检查当前 Git 状态，再根据用户的新要求继续；尚未指定实验 06，不自行跳到真实模型或 Tool Calling。

## 12 建立 AI 工作日志

**问题：维护 AI_LOG.md，按“问题--回答”记录 Codex 工作经历，便于其他代理接续。** -- **回答：** 读取时该文件为空，现将当前对话中可确认的项目初始化、Git 修复、网络诊断、实验 01–05、一次授权提交推送和当前工作状态写入此文件。本次仅维护 `AI_LOG.md`，不修改实验与其他文档，不执行 commit 或 push。后续记录应追加新的问题、实际改动、验证结果及未完成事项，明确区分计划与已经完成的操作。

## 13 独立部署 Ollama 与本地模型

**问题：在 Windows 11 上部署适合 Agent 学习的本地 LLM，部署期间不要修改 MCP_SKILL。** -- **回答：** 先做只读检查：Windows 11 专业版 Build 26200、Python 3.10.11 64 位、RTX 5060（8151MiB 显存）、NVIDIA 驱动 616.56 均正常；最初未发现 Ollama 安装或服务。

用户随后授权安装，使用 winget 的 `Ollama.Ollama` 包，从 Ollama 官方 GitHub 下载并校验安装器，成功安装 0.34.4。路径为 `C:\Users\Administrator\AppData\Local\Programs\Ollama\ollama.exe`。本地 `http://localhost:11434/`、`/api/version`、`/api/tags` 均返回 HTTP 200，服务监听 `127.0.0.1:11434`。安装过程无需人工点击，提醒用户重新打开 VS Code 以更新 PATH。

先比较 qwen3:4b、qwen3:8b、qwen2.5:7b，等用户明确选择 `qwen3:8b` 后才下载，只下载这一个模型。`ollama list` 确认 ID 为 `500a1f067a9f`，大小约 5.2GB；实测 `ollama ps` 显示 100% GPU、4096 上下文、加载大小约 5.6GB。模型文件默认位于 `%USERPROFILE%\.ollama\models`。以上版本和硬件状态均为当时实测，不代表后续自动保持不变。

## 14 OLLAMA_LOCAL 的 CLI、API 与 Python 验证

**问题：验证本地模型，并提供返回字符串的 call_llm(prompt) 接口。** -- **回答：** 确认独立目录 `E:\projects_mcp_skill\OLLAMA_LOCAL` 存在且为空，在该目录创建 `README.md`、`requirements.txt`、`ollama_client.py` 及 `tests/01_basic_chat.py`、`tests/02_action_decision.py`、`tests/03_call_llm_function.py`。使用 Python 标准库 urllib，无第三方依赖，不实现 Agent Loop。

客户端通过 `POST http://localhost:11434/api/generate` 调用 qwen3:8b，使用 `stream=false`、`think=false`、temperature=0、num_ctx=4096，并返回 response 文本；处理连接失败、HTTP 错误、模型不存在、空响应、无效 JSON、超时和截断，不自动重试。

命令行中文介绍正常。原始动作题仅列出动作和 current=1、target=6，模型返回 `increment`，并非 double；明确“翻倍不超过目标时优先 double”后，两个 Python 动作测试均返回 `double`。API 输入“你好，请只回复：本地 API 正常。”，实际返回“本地 API 正常。”，HTTP 200，已加载模型的该次请求约 2.33 秒。错误处理通过 mock 模拟检查，未停止真实服务或删除模型。

用户询问如何运行时，给出在 OLLAMA_LOCAL 根目录执行 `python -X utf8 tests/01_basic_chat.py`、`python -X utf8 tests/02_action_decision.py`，以及直接聊天命令 `ollama run qwen3:8b --think=false`（输入 `/bye` 退出）。这段部署和测试工作没有修改 MCP_SKILL；之后用户另行明确授权在主项目创建实验 06。

## 15 实验 06：Real LLM Decision with Ollama

**问题：把实验 05 的 Fake LLM 替换为真实 qwen3:8b 决策，保留 Agent Loop 并增加保护。** -- **回答：** 根据用户附件创建 `01-agent/examples/06_real_llm_decision.py`，沿用 current=1、target=6、四个候选动作及 double 最多一次的任务。前五个实验文件未修改。

架构为 `Context → Prompt → Ollama API → qwen3:8b → LLM Response → parse_action → Action → execute → Observation`。`decide(context)` 只构造 Prompt、调用模型、打印响应、解析并返回动作，没有 Python 决策回退。使用标准库独立实现 call_llm，不导入 OLLAMA_LOCAL 的文件；不需要添加 requests 或其他依赖。

请求地址为 `http://localhost:11434/api/generate`，模型为 qwen3:8b，非流式、think=false、temperature=0、num_ctx=4096、num_predict=128，单次请求超时 120 秒。处理无法连接、超时、异常状态码、无效 JSON、缺少 response、非文本或空内容和截断等错误。

parse_action 采用严格方案：规范化大小写、首尾空白和换行，接受简单成对引号、行内代码、强调或纯文本代码块包裹；完整内容必须对应一个合法动作，不从解释性句子猜答案。validate_action 只拒绝违规建议，不代选动作：阻止动作空间之外的名称、超次数 double 和未到目标时 stop。execute 仍拒绝未知动作，模型不能直接修改 State。

`MAX_STEPS=10` 包含 stop，在第 11 次模型调用前终止；失败打印 `Task failed` 并返回非零退出码，不报告假成功。

## 16 实验 06 的首次失败与成功验证

**问题：真实模型是否遵守规则，运行失败后如何处理？** -- **回答：** 运行前确认 qwen3:8b 已安装、Ollama API 正常（版本 0.34.4）。首次运行：第 1 轮 double 成功，从 1 到 2；第 2 轮模型再次返回 double，名称解析成功，但被次数校验拦截，未执行第二次翻倍。

问题归类为 LLM 任务规则遵循问题，不是 Ollama 服务、网络、JSON 或动作格式问题。只修改 Prompt，显式展示剩余 double 次数，并列出按顺序判断的规则，突出次数为0时禁止 double。没有改变架构、关闭校验、增加自动重试或用 Python 替模型生成答案。

修改后的真实运行结果：

| 轮次 | 模型原始响应 / 解析结果 | 执行后 current | finished |
| --- | --- | --- | --- |
| 1 | double | 2 | False |
| 2 | increment | 3 | False |
| 3 | increment | 4 | False |
| 4 | increment | 5 | False |
| 5 | increment | 6 | False |
| 6 | stop | 6 | True |

最后输出 `Task completed.`、`Total steps: 6`。本次成功运行解析全部通过、double 执行一次、未触发 MAX_STEPS、没有非法格式响应或 API 异常；这不保证后续模型永远正确。

另外用模拟响应检查了格式规范化、非法文本拒绝、未知动作与业务规则拦截、MAX_STEPS（故意连续模拟 decrement，确认恰好调用10次后停止）、连接/HTTP/超时/JSON/缺字段/空响应等错误分支，均通过。模拟测试与上述真实模型运行分开进行，没有把模拟结果报告为模型输出。

更新了 `01-agent/README.md` 和 `01-agent/notes/agent-basics.md`，记录 Real LLM Decision 的分工、保护与实际失败原因。哈希检查确认前五个实验、根 README.md 和 LEARNING_ROADMAP.md 未修改。未执行 commit 或 push。

## 17 实验 06 完成时的接续状态（历史快照）

**问题：同步更新 AI_LOG，后续代理现在应该从哪里继续？** -- **回答：** 本次仅更新此日志，补充第 13–17 条，并将第 11 条标注为历史快照。当前已完成阶段 01 的实验 01–06，实验 06 已接入真实本地模型；尚未实现 Tool Calling、MCP、Skill 或大型 Agent 框架。不能继续沿用旧快照中“只有 Fake LLM、尚未指定实验06”的状态。

本次只读检查显示：分支 main，HEAD 为 `e54a99b`，与本地保存的 origin/main 跟踪信息一致；未联网核实远程最新状态。阶段 README、基础笔记、FRUITS.md 有未暂存修改；实验 04、05、06 和 AI_LOG.md 尚未跟踪。不要覆盖用户 FRUITS.md 的改动，也不要自动暂存、提交或推送。

接续时先阅读本日志最新记录、阶段 README 和基础笔记，再检查文件及 Git 状态。复现实验 06 可在 MCP_SKILL 根目录执行 `python -X utf8 01-agent/examples/06_real_llm_decision.py`，先确认 Ollama 服务与 qwen3:8b 可用。本次日志同步未重新运行模型；运行结果来自上一项已完成实验。下一实验尚未指定，等待用户的新任务。

## 18 实验 07：LLM Failure & Recovery 与最新接续状态

**问题：模型输出失败时，如何拒绝、反馈、重试并恢复，避免无限循环？** -- **回答：** 新增 `01-agent/examples/07_llm_failure_recovery.py`，沿用实验 06 的独立标准库 HTTP 客户端、真实 Ollama qwen3:8b、Parser、Validator 和执行循环，未修改前六个实验。新增 `decide_with_retry(context)`，`MAX_RETRIES=2` 允许首次加两次重试，仍失败则明确报错；`MAX_STEPS=10` 限制 Agent Step，重试不增加 Step。

每次尝试保存原始模型响应、实际待验证响应、是否注入、解析动作、校验结果、失败阶段与原因；Decision Attempts 按 Step 独立记录，Execution History 只收录成功执行的动作。请求失败、非法动作、多动作、解释性输出、超次数 double、提前 stop 均不得执行。失败时把响应与具体原因加入下一次 Prompt，再次真实调用模型，程序不自动替换为正确动作。

默认 `FORCE_FAILURE_DEMO=True`，仅 Step 2 / Attempt 1 人为注入；默认路径用 double 触发 Validator 拒绝。如果第一步未使用 double，则用 jump 触发 Parser 拒绝，确保演示确实失败。注入与真实输出分开显示，关闭开关即可测试不注入的真实行为。

本次运行前确认模型存在，Ollama API 版本 0.34.4 正常。实际结果：

- Step 1：真实返回 double，执行后 current=2。
- Step 2 / Attempt 1：真实返回 increment；人为替换成 double；Parser 接受名称，但 Validator 拒绝“double 已达到使用上限”；未执行、未更新 State 或 Execution History。
- Step 2 / Attempt 2：附带失败反馈重新请求，真实返回 increment，通过校验，执行后 current=3。
- Step 3–5：真实返回 increment，依次到达 4、5、6。
- Step 6：真实返回 stop，finished=True，任务完成。

最终输出：`Total steps: 6`、`Decision attempts: 7`、`Total retries: 1`、`Execution history entries: 6`。发生一次人为失败并恢复，未耗尽 MAX_RETRIES，未触发 MAX_STEPS，没有真实服务或模型异常。

另做模拟边界检查：六种失败都能带反馈重新请求且保持状态/执行历史不变；连续失败恰好尝试 3 次后终止；一直选择合法 decrement 在第 10 步后停止；注入前后响应和两类历史没有混淆。以上检查通过，未把模拟输出当作真实模型结果。

同步更新阶段 README、基础笔记和本日志。未安装依赖、未执行 commit/push、未修改根 README 或 LEARNING_ROADMAP。用户 FRUITS.md 的已有改动保留。下一实验尚未指定；接续先检查当前 Git 状态与 Ollama 服务，运行命令为 `python -X utf8 01-agent/examples/07_llm_failure_recovery.py`。

## 19 阶段 01 文档收尾

**问题：完成 Agent 阶段复盘，使仓库说明实验 01–07 的学习成果与下一阶段。** -- **回答：** 将 `01-agent/README.md` 整理为七个实验的阶段总览、当前能力、运行方式与下一阶段入口；将 `01-agent/notes/agent-basics.md` 按概念演进重组为复习笔记，覆盖 Goal、State、Context、History、Action、Observation、Prompt、Parser、Validator、Executor、Retry、Runtime 等，并给出纯文本架构图。保留历史实验实例及实验 06 的真实违规建议、实验 07 的人为注入与恢复结果。

根 README 只更新当前进度，`LEARNING_ROADMAP.md` 仅将 `01-agent` 标为 Completed、`02-tool-calling` 标为 Next 并记录已完成主题。此日志在顶部新增 Project Identity、Learning Method、Environment、Repository Status、Completed Experiments、Key Architecture Learned、Important Design Decisions、Current Agent Architecture、Codex Working Rules、Next Objective；原有问答保留在 Historical Conversation Log。阶段 01 的学习内容现可视为完成，阶段 02 尚未开始。文档架构图按代码顺序在更新 State 之前保存 `state_before`。

本次只整理文档，不修改实验 01–07 的代码逻辑，不新增 Experiment 08、Tool Calling、MCP 或 Skill 实现，也未安装依赖、执行 commit 或 push。以后继续工作时以最新 Git 状态和实际文件为准。
