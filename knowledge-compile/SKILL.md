---
name: knowledge-compile
description: >
  下午知识整理入库。每周一至五 14:00 自动执行。
  从探照灯文章摘要提取有价值内容，整理成知识点写入知识库，
  并更新当日 memory/YYYY-MM-DD.md。
license: MIT
---

# 下午知识整理

## 任务目标

读取探照灯今日文章 → 提取有价值的发现 → 写入知识库 → 更新记忆文件

## 执行步骤

### 1. 读取探照灯文章
```bash
cat /tmp/spotlight_articles.txt 2>/dev/null || echo "文件不存在，跳过"
```
如果文件不存在或为空，直接结束。

### 2. 整理有价值的发现
从文章中提取：
- 有数据支撑的新认知
- 有启发性的观点
- 有实操价值的技巧

### 3. 写入知识库
追加到 `~/.openclaw/workspace/skills/dbskill/知识库/原子库/atoms_2026Q1.jsonl`

```bash
echo '{"date":"YYYY-MM-DD","title":"...","tags":["...","..."],"summary":"...","insight":"..."}' >> ~/.openclaw/workspace/skills/dbskill/知识库/原子库/atoms_2026Q1.jsonl
```

### 4. 更新当日 memory 文件
```bash
echo -e "\n## 下午知识整理\n- 整理了 X 条知识点" >> ~/.openclaw/workspace/memory/YYYY-MM-DD.md
```

### 5. 记录日志
```bash
bash ~/.openclaw/scripts/shared_log.sh '爪巴' '下午知识整理' '已完成' '已整理X条知识点'
```

## 注意事项

- 没有有价值内容时，直接结束，不要硬凑
- 只写有实质内容的发现
- 知识库写入后确认文件更新成功
