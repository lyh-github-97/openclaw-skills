---
name: self-reflect
description: GEPA轻量版：AI任务执行后自动写反思到缓冲区，每日定时批量合成改进建议，人类确认后更新SOUL.md。触发词：反思/回顾/改进建议
---

# Self Reflect

GEPA 自我进化系统的轻量实现：执行 → 反思 → 改进，三步闭环。

## 核心文件

- **反思缓冲区**：`memory/reflect-buffer.md`
- **改进建议**：`memory/reflect-suggestions.md`（每日cron生成）
- **最终写入**：`SOUL.md` / `AGENTS.md`

## 触发词

遇到以下情况，立即执行，不等待：
- 任务失败或出错
- 发现值得记住的教训（错误、根因、解决方案）
- 用户说"反思"/"回顾"/"改进建议"

## 执行步骤

### 立即反思（出错时）

1. 写一行到 `memory/reflect-buffer.md`：
   ```markdown
   ## [反思] YYYY-MM-DD HH:MM

   **任务**：<简述>
   **问题**：<根因分析>
   **改进**：<具体建议>
   ```

### 批量合成（每日 cron）

脚本：`scripts/batch_analyze.py`
- 读取 `reflect-buffer.md`
- 找出重复失败模式
- 生成改进建议到 `reflect-suggestions.md`
- 推送人类确认

### 人类确认后写入

确认后执行 `scripts/apply_suggestions.py`，将建议写入 SOUL.md。

## 核心原则

- 自动化生成，人工确认后才写入
- 每次反思不超过3行
- 批量比实时更有效
