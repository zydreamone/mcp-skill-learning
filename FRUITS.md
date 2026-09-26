# 此文件用于记录一些chatgpt的回答，用于理解

## 1.
LLM：负责理解、推理、生成“下一步该做什么”
Agent：负责把这个“下一步”真正执行，并根据执行结果继续决定下一步
Tool：Agent 用来执行现实动作的接口

## 2.
TODO 可以理解成程序员给自己留下的“待办事项”标记

## 3.
State= 当前任务处于什么状态

Context= Agent 当前做决策时知道哪些信息

## 4.
Goal / Rules / Available Actions / State / History

## 5.
LLM
负责 Decision

Runtime
负责 Loop

Parser
负责解析

Validator
负责约束

Executor
负责执行

State
负责保存当前状态

History
负责保存过去

Context
负责组织决策信息