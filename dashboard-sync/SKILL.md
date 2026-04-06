---
name: dashboard-sync
version: 1.0.0
description: 同步 OpenClaw Skills 和工作仪表盘，确保 Bitable 记录与实际安装状态一致。触发条件：手动调用 或 每次安装/卸载 skill 后主动执行。
---

# Dashboard Sync 🔄

## 功能
将 `~/.openclaw/skills/` 目录与 Skills 管理仪表盘（Bitable）进行双向同步，确保记录与实际一致。

## 仪表盘信息
- Skills 管理仪表盘 app_token: `LSSfbiIyYabOvzsyHxbcxTjFnIg`
- Skills 管理仪表盘 table_id: `tblaPz9guHgEphmk`
- 工作仪表盘 app_token: `HESBb9gSbabP9JsmssCcJRUJnmb`
- 工作仪表盘 table_id: `tblakR4xtzfoxQxZ`

## 同步逻辑

### 获取 Skills 目录实际状态
读取 `~/.openclaw/skills/` 和 `~/.openclaw/workspace/skills/`，收集所有 skill 名称。

### 获取仪表盘当前记录
用 `feishu_bitable_list_records` 读取两个仪表盘所有记录。

### 对比差异
- 仪表盘有但目录没有 → 从仪表盘删除记录
- 目录有但仪表盘没有 → 仪表盘新增记录
- 都有但信息不同 → 更新仪表盘记录

### 字段规范（Skills 仪表盘）
- 技能名称: skill 目录名
- 功能描述: 从 SKILL.md 读取 description 字段，无则留空
- 关联Agent: 从 path 推断（~/.openclaw/skills/ → 爪巴，~/.openclaw/agents/{agent}/ → 对应agent）
- 用途/触发词: 从 SKILL.md 读取，无则留空
- 备注: 版本/安装时间/来源
- 类型: 根据 skill 名称推断（名称含 cron → cron，含 research/report → 研究，其余 → 工具）
- 安装状态: 固定"已安装"

### 字段规范（工作仪表盘）
- 任务名称: 任务名称
- 状态: 待处理 / 进行中 / 已完成 / 暂停
- 优先级: 高 / 中 / 低
- 负责人: 爪巴 / 研研 / 财财 / 探照灯 / L
- 备注: 结论/完成时间/原因
- 截止日期: 有则填，无则空

## 使用方式
手动触发（直接告诉我"同步仪表盘"）或安装/卸载 skill 后自动调用。

## 执行脚本
同步逻辑由 `scripts/sync.py` 执行（Python 3，无第三方依赖）。
