---
name: launcher-guardian
description: LaunchAgent看护 — 每日自动巡检所有openclaw定时任务，自动诊断、自动修复、自动重触发，不请示。触发词：巡检定时任务 / 检查定时任务
---

# launcher-guardian

每日自动（09:00/13:00/17:00/21:00）巡检所有 openclaw 相关 LaunchAgent，发现失败立即修复并推送报告。

## 核心职责

1. **状态巡检**：遍历所有 `ai.openclaw.*`、`com.openclaw.*`、`com.爪巴.*` LaunchAgent，读取 `launchctl list` 状态
2. **日志扫描**：读取 `~/.openclaw/logs/`，识别 ERROR/Traceback/failed/syntax error 等关键字
3. **自动诊断**：识别失败模式（见下表）
4. **自动修复**：对每种模式执行对应修复，无需请示
5. **重触发**：修复成功后 `launchctl bootout` + `load`，验证恢复
6. **飞书推送**：汇总报告推送财财窗口

## 已知失败模式 & 修复方案

| 模式 | 检测关键词 | 修复方案 |
|------|-----------|---------|
| nvm.sh return 11 | nvm/npmrc/return 11/set -e | 行首直接 source 包裹子shell隔离 |
| plist XML 标签损坏 | mismatched tag/Format error | plistlib 重序列化 |
| 记忆文件缺失 | 找不到记忆文件 | 创建空文件 |
| node 路径缺失 | node not found | PATH 追加绝对路径 |
| python 路径缺失 | python not found | PYTHON_PATH 环境变量修复 |

## 已知问题 Agent 配置

| Agent | 日志文件 | 修复类型 |
|-------|---------|---------|
| diary-full | diary-full.log | nvm_return |
| diary-collect | diary-collect.log | nvm_return |
| morningreport | morning_report.log | nvm_return |
| eveningreport | evening_report.log | nvm_return |
| spotlight-collect | spotlight-collect.log | nvm_return |
| skills-backup | skills_backup.log | nvm_return |
| memory-backup | backup-memory.log | nvm_return |
| deep-research | deep-research.log | nvm_return |
| ft-sync | ft_to_feishu.log | nvm_return |
| zlib-nightly | zlib-nightly.log | nvm_return |
| bb-browser | bb-browser.log | nvm_return |
| ai-weekly-report | ai-weekly-report.log | nvm_return |
| apiquota | apiquota.log | nvm_return |
| backup | backup.log | nvm_return |
| vpn-monitor | vpn-monitor.log | nvm_return |
| local-memory-curate | local-memory-curate.log | python_path |
| memory-archive | memory-archive.log | python_path |
| dashboard-fill | dashboard-fill.log | python_path |
| dashboard-check | dashboard-check.log | python_path |

## 使用方式

自动调度（每日 09:00/13:00/17:00/21:00）：

```bash
/usr/bin/python3 ~/.openclaw/skills/launcher-guardian/scripts/cron_guardian.py
```

手动触发（任何时候）：

```bash
/usr/bin/python3 ~/.openclaw/skills/launcher-guardian/scripts/cron_guardian.py
```

## 输出

- 飞书报告 → 财财窗口（`oc_672b6574c3477985a1a517f748d3dd4a`）
- 结构：正常 / 已修复 / 未解决 三个分类

## Workflow

1. 读取所有 LaunchAgent 状态
2. 扫描日志识别错误模式
3. 对识别出的问题执行对应修复
4. 重新加载 LaunchAgent
5. 生成报告推送飞书
