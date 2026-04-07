---
name: bb-browser
description: >
  bb-browser 是 AI Agent 的浏览器自动化工具，通过 CDP 直连 Chrome。
  核心能力：126个 site adapter 直接获取结构化数据（Hacker News/GitHub/知乎等），
  无需登录态抓取。触发词：bb-browser、HackerNews、GitHub trending、arxiv搜索。
conditions:
  requires_tools: browser
  fallback_reason: 当 browser tool 不可用时，跳过结构化数据获取
---

# bb-browser Skill

## 核心价值

bb-browser = 真实浏览器 + 结构化数据适配器。比 web_search 更精准，比爬虫更稳定。

## 前提条件

Chrome 需先启动（独立实例，不影响 OpenClaw 浏览器 session）：

```bash
# 启动 Chrome（监听 19825）
open -n "/Applications/Google Chrome.app" --args \
  --user-data-dir=/Users/liyaohua/.bb-chrome \
  --remote-debugging-port=19825 \
  --no-first-run

# 启动 daemon（自动连接 Chrome CDP）
bb-browser daemon start
```

**注意**：daemon 只需启动一次，Chrome 重启后 daemon 自动重连。

## 常用命令

### 数据获取（site adapter）
```bash
bb-browser site hackernews/top 10        # Hacker News 热门
bb-browser site hackernews/new 5        # 最新
bb-browser site hackernews/thread <id>  # 指定帖子
bb-browser site arxiv/search "关键词" 5  # arxiv 论文搜索
bb-browser site github/trending         # GitHub trending
bb-browser site github/repo <owner/repo> # 仓库信息
bb-browser site bilibili/search "关键词" 5 # B站搜索
bb-browser site zhihu/hot 5             # 知乎热榜
bb-browser site v2ex/hot               # V2EX 热门
bb-browser site list                   # 查看所有 adapter
```

### 浏览器操作
```bash
bb-browser open <url> [--tab]           # 打开 URL
bb-browser snapshot                      # 页面快照（带可交互元素引用）
bb-browser screenshot [path]           # 截图
bb-browser tab list                     # 查看所有标签页
bb-browser tab new                      # 新建标签页
bb-browser tab close <id>               # 关闭标签页
bb-browser status                       # 查看浏览器状态
```

### 调试
```bash
bb-browser network requests             # 查看网络请求
bb-browser console                      # 控制台输出
bb-browser errors                       # JS 错误
bb-browser guide                        # 如何写新 adapter
bb-browser site info <name>            # 查看 adapter 详情
```

## 认证需求

| 平台 | 状态 | 说明 |
|------|------|------|
| Hacker News | ✅ 直接用 | 无需登录 |
| arxiv | ✅ 直接用 | 无需登录 |
| GitHub | ✅ 直接用 | 无需登录 |
| V2EX | ✅ 直接用 | 无需登录 |
| 知乎 | ✅ 直接用 | 无需登录 |
| B站 | ✅ 直接用 | 无需登录 |
| Twitter/X | ❌ 需要登录 | 需先在 Chrome 中登录 x.com |
| 微博 | ⚠️ 部分可用 | 部分 adapter 需要登录 |

## daemon 管理

```bash
# 查看 daemon 状态
bb-browser daemon status

# 停止 daemon
bb-browser daemon stop

# 重启（Chrome 重启后）
bb-browser daemon start

# daemon 配置位置
~/.bb-browser/daemon.json
```

## 与现有工具对比

| 工具 | 优点 | 缺点 |
|------|------|------|
| bb-browser | 结构化数据、126个adapter、CDP直连 | 需独立Chrome实例、daemon需常驻 |
| autocli | 命令丰富（50+）、零依赖 | 知乎/微博等需Chrome扩展 |
| web_search | 覆盖广、简单 | 无结构化、结果粗糙 |
| browser tool | OpenClaw内置 | 操作复杂、无adapter |

## 适用场景

- **信息获取首选 bb-browser**：HackerNews/arxiv/GitHub/知乎/B站 → 直接结构化输出
- **autocli 备选**：Twitter/微博/小红书等平台
- **web_search 兜底**：搜索引擎类、无 adapter 的网站
