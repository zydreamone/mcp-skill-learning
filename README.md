# MCP & Skill Learning

用于系统学习 Agent、Tool Calling、Skill、MCP Server、MCP Client 及其综合应用的 Python 学习项目。

本项目采用 **理论 + 实验 + Codex 辅助** 的方式：先理解概念，再完成最小实验，记录观察与问题，最后整理代码和文档。Codex 用于解释概念、辅助实现和检查结果；每一步都应能够自行理解和复现。

这是一个逐步演进的学习项目，不是一次性完成的大型工程。只在进入相应阶段时添加必要代码和依赖。

## 学习路线与目录

按 Foundation → Agent → Tool Calling → Skill → MCP Server → MCP Client → 综合应用 → 真实场景 → 最终项目的顺序推进。详见 [学习路线](LEARNING_ROADMAP.md)。

| 目录 | 用途 |
| --- | --- |
| `00-foundation/` | 项目结构、Git、Python、API / JSON / CLI 基础 |
| `01-agent/` | Agent Loop、状态、上下文、行动与观察 |
| `02-tool-calling/` | 工具定义、参数、返回值和工具选择 |
| `03-skill/` | Skill 结构及多步骤任务组织 |
| `04-mcp-server/` | MCP 协议与服务端能力暴露 |
| `05-mcp-client/` | 连接服务端、发现与调用工具 |
| `06-agent-skill-mcp/` | Agent + Skill + MCP 小型综合实验 |
| `07-real-world-mcp/` | 文件系统、GitHub、API、数据库与多服务端 |
| `08-final-project/` | 逐步构建 Developer Assistant Agent |
| `docs/` | 核心概念索引与 `notes/` 学习笔记 |
| `shared/` | 后续按需提取的公共 `tools/`、`utils/`、`config/` |
| `playground/` | 临时探索和小实验 |

各阶段的 `examples/` 用于后续实验；`03-skill/skills/` 保存后续 Skill；`04-mcp-server/servers/` 保存后续服务端；`08-final-project/src/` 保存最终项目源码。空目录中的 `.gitkeep` 仅用于 Git 保留目录。

## 当前状态

当前进度：`00-foundation` 已完成项目结构与基础配置；`01-agent` 已完成实验 01–07，详见 [阶段总览](01-agent/README.md)；`02-tool-calling` 是下一阶段。后续阶段仍待学习，未引入 LangChain、LangGraph 等大型框架。

## 推荐环境

- Windows 11、PowerShell、VS Code
- Python 3.10+、Git
- 按后续实验需要再配置模型 API 和凭据

在项目根目录使用 PowerShell 创建环境：

```powershell
py -3 --version  # 确认版本 >= 3.10
py -3 -m venv .venv
.\.venv\Scripts\python.exe --version
```

在 VS Code 中选择 `.venv\Scripts\python.exe` 作为解释器。当前无需安装依赖，也无需执行 `pip install .`；`pyproject.toml` 仅记录基础项目元数据，打包配置留待有实际需求时添加。

建议每次学习记录“问题 → 实验 → 观察 → 结论 → 下一步”，确认理解后再进入下一阶段。概念入口见 [核心概念](docs/concepts.md)。不要将 API 密钥提交到仓库。

## GitHub

仓库地址：https://github.com/zydreamone/mcp-skill-learning.git

提交与推送由学习者自行决定；初始化不自动执行 commit 或 push。
