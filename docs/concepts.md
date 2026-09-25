# 核心概念索引

当前仅提供一句话定义，后续随实验逐步补充示例与边界。

| 概念 | 简短定义 |
| --- | --- |
| LLM | 大语言模型是根据输入上下文生成和处理语言内容的模型。 |
| Agent | Agent 是围绕目标选择行动、接收反馈并推进任务的系统。 |
| Tool | Tool 是可被调用以执行具体操作的程序能力。 |
| Tool Calling | Tool Calling 是模型提出结构化工具调用请求、由应用执行并回传结果的过程。 |
| Skill | 本项目中的 Skill 是面向一类任务、组织指令、步骤和所需资源的可复用能力单元。 |
| MCP | MCP（Model Context Protocol）是应用与外部工具及上下文来源交互的标准化协议。 |
| MCP Server | MCP Server 是通过 MCP 暴露工具、资源或提示模板等能力的服务端。 |
| MCP Client | MCP Client 是由宿主应用使用、负责与 MCP Server 建立连接并交互的协议组件。 |
| Resource | Resource 是 MCP Server 提供给客户端读取的上下文数据。 |
| Prompt | Prompt 是引导模型行为的输入指令，在 MCP 中也指服务端提供的可复用提示模板。 |
| Context | Context 是模型在一次处理时可使用的指令、消息及其他输入信息。 |
| State | State 是系统为持续执行任务而维护的当前运行数据。 |
| Memory | Memory 是供后续步骤或会话检索与复用的历史信息。 |
