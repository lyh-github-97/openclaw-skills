# memory-archive skill - 记忆归档

## 功能
定期将 MEMORY.md 中超过 30 天的条目自动归档到 `memory/archive/YYYY-MM.md`，保持 MEMORY.md 只保留近期记忆。

## 触发词
归档记忆、archive memory、整理记忆

## 运行方式
手动触发，或通过 cron 定期运行（建议每周一执行）

## 执行步骤

### 1. 检查 MEMORY.md
读取 `~/.openclaw/workspace/MEMORY.md`，解析所有带 `YYYY-MM-DD` 时间戳的条目。

### 2. 判断是否需要归档
- 条目时间 < 30 天 → 保留在 MEMORY.md
- 条目时间 ≥ 30 天 → 归档到 `memory/archive/YYYY-MM.md`

### 3. 执行归档
- 在 `memory/archive/` 下按月创建归档文件（如 `2026-03.md`）
- 被归档的条目从 MEMORY.md 中移除
- 归档文件格式：每个条目保留原始文本，顶部加 `## YYYY-MM-DD 归档` 标记

### 4. 输出摘要
输出：归档了多少条、涉及哪些主题、当前 MEMORY.md 条目数量

## 安全规则
- **不删除任何内容**，只移动到归档文件
- 保留 MEMORY.md 顶部的重要规则区（# 重要规则 标题下的所有内容）
- 归档前先备份 MEMORY.md 到 `memory/MEMORY.md.bak`

## 依赖
- Python 3，无第三方库
- 需要可写的 `memory/archive/` 目录
