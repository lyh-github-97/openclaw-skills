---
name: local-memory
version: 1.0.0
description: 本地结构化记忆系统。模仿 ByteRover 三层记忆架构，数据完全存储在本地（~/.openclaw/skills/local-memory/knowledge/），不依赖任何外部服务。
---

# Local Memory 🧠

## 架构（三层）

### 第一层：原始记忆
`~/.openclaw/workspace/memory/YYYY-MM-DD.md` — 每日原始记录

### 第二层：结构化知识树
`~/.openclaw/skills/local-memory/knowledge/knowledge_tree.json`
- 按分类组织（config/error/pattern/knowledge/task/decision）
- 每条记忆带时间戳、来源、标签、置信度
- 可追溯的决策路径

### 第三层：检索
`retrieve.py` — 根据当前问题检索相关记忆

---

## 核心脚本

### curate.py — 知识挖掘
从 memory/ 文件提炼知识存入知识树

```bash
python3 ~/.openclaw/skills/local-memory/scripts/curate.py --since 3  # 最近3天挖掘
python3 ~/.openclaw/skills/local-memory/scripts/curate.py --all        # 全部重新挖掘
python3 ~/.openclaw/skills/local-memory/scripts/curate.py --summary "L的配置偏好" --cat pattern  # 手动添加
```

### retrieve.py — 记忆检索
根据问题检索相关记忆

```bash
python3 ~/.openclaw/skills/local-memory/scripts/retrieve.py "L的配置偏好"
python3 ~/.openclaw/skills/local-memory/scripts/retrieve.py --cat error --limit 3  # 只查错误教训
python3 ~/.openclaw/skills/local-memory/scripts/retrieve.py --all  # 列出最近20条
```

---

## 分类说明

| 分类 | 说明 |
|------|------|
| config | 系统配置、技术选型决策 |
| error | 犯过的错及修复方案 |
| pattern | L 的偏好、工作习惯、沟通模式 |
| knowledge | 学到的新知识、认知更新 |
| task | 成功执行过的任务流程 |
| decision | 重要决策及理由 |

---

## 使用时机

### 每日定时（LaunchAgent）
每天 22:00 自动运行 `curate.py --since 1`，从当日 memory 提炼知识

### 每次会话开始
优先调用 `retrieve.py` 获取相关记忆，作为上下文参考

### 重要决策后
手动调用 `curate.py --summary "..." --cat decision` 立即沉淀

### Context 压缩前（待 OpenClaw 支持 hook）
compaction 触发时自动运行，保存关键洞察

---

## 路径

- 知识树：`~/.openclaw/skills/local-memory/knowledge/knowledge_tree.json`
- 脚本：`~/.openclaw/skills/local-memory/scripts/curate.py` + `retrieve.py`
- memory 源：`~/.openclaw/workspace/memory/`
