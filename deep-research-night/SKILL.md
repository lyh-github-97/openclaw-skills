---
name: deep-research-night
description: >
  深夜深度研究 + 知识库写入。每周一至五 01:00 自动执行。
  从 claw123.com / hengclaw.com / Twitter/X 搜索 AI/OpenClaw/Agent 领域最新内容，
  深入研究最有价值的3个选题，整理成知识点写入 atoms_2026Q1.jsonl。
license: MIT
---

# 深夜深度研究

## 任务目标

读取知识库了解现状 → 搜索最新有价值内容 → 深入研究 → 写入知识库

## 执行步骤

### 1. 读取知识库当前状态
```bash
tail -20 ~/.openclaw/workspace/skills/dbskill/知识库/原子库/atoms_2026Q1.jsonl
```
了解最新日期和已有知识点，避免重复。

### 2. 搜索最新内容
从以下来源搜索有价值的选题：
- claw123.com
- hengclaw.com  
- Twitter/X 搜索 AI/OpenClaw/Agent 相关

关键词参考：OpenClaw skill / MCP / AI agent / memory system / 最新模型

### 3. 深入研究（web_search）
选择最有价值的3个选题，每个深度调研：
- 背景和原理
- 最新动态
- 各方观点
- 数据支撑

### 4. 写入知识库
追加到 `~/.openclaw/workspace/skills/dbskill/知识库/原子库/atoms_2026Q1.jsonl`

格式（一行 JSON）：
```json
{"date":"YYYY-MM-DD","title":"标题","tags":["tag1","tag2"],"summary":"核心内容3-5句","insight":"对我的启发"}
```

### 5. 记录到日志
```bash
bash ~/.openclaw/scripts/shared_log.sh '爪巴' '深夜深度研究' '<研究主题>' '<核心发现>'
```

## 注意事项

- 知识点要有实质性内容，不是泛泛而谈
- 优先选有数据支撑、有多方观点的选题
- 写完知识点后立即写入文件，不要只存在内存里
