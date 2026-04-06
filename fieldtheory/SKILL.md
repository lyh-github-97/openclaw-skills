---
name: fieldtheory
description: "X/Twitter 书签本地同步和搜索。读取 ~/.ft-bookmarks/，让我能直接查询你收藏的内容。触发词：X书签、Twitter书签、同步书签、书签搜索、看看我收藏了哪些"
---

# Field Theory CLI — X 书签本地同步

把你的 X/Twitter 收藏同步到本地 `~/.ft-bookmarks/`，让我能直接搜索你积累的内容。

## 安装确认

CLI 已安装：`which ft` → `/Users/liyaohua/.npm-global/bin/ft`
版本：`ft --version`

## 核心命令

### 同步书签
```bash
ft sync                    # 增量同步（默认）
ft sync --full            # 全量重新爬取
ft sync --classify        # 同步后用 LLM 分类
```

### 搜索
```bash
ft search "<关键词>"      # BM25 全文搜索
```

### 查看
```bash
ft list                   # 列出所有书签
ft list --category tool    # 按分类筛选
ft show <id>             # 看单条详情
ft categories             # 分类分布
ft domains                # 域名分布
ft stats                  # 统计（作者/语言/日期范围）
```

### 数据位置
```
~/.ft-bookmarks/
  bookmarks.jsonl    # 原始缓存
  bookmarks.db       # SQLite FTS5 搜索索引
  bookmarks-meta.json # 同步元数据
```

## Skill 用途

**触发场景：**
- L 提到"我之前在 X 上看到过关于 XXX 的内容"
- 深度研究时，主动查 L 的相关书签库作为补充
- 做 AI/技术分析时，把 L 收藏的相关内容一起参考

**工作流程：**
1. `ft search "<L 提到的关键词>"`
2. 分析结果，给 L 有针对性的回答
3. 发现有价值的新内容 → 建议 L 收藏

## Cron 任务

每日自动同步，08:30 运行（早餐时间，同步昨天的内容）。

触发条件：必须 Chrome 登录 X 才有效（session sync 模式）。
如 Chrome 未登录，跳过同步并记录到日志。

## 注意事项

- Chrome session sync 仅 macOS 支持，Linux/Windows 需用 OAuth API 模式
- `ft sync --classify` 每次会调 LLM API（注意 token 消耗）
- OAuth token 存储在 `~/.ft-bookmarks/oauth-token.json`，chmod 600
