#!/bin/bash
# 探照灯内容发现脚本
# 输出到 /tmp/spotlight_raw.md

export PATH="/Users/liyaohua/.nvm/versions/node/v22.22.0/bin:$HOME/.nvm/versions/node/v22.22.0/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/liyaohua"
export USER="liyaohua"

CACHE_FILE="/tmp/spotlight_raw.md"
ARTICLES_FILE="/tmp/spotlight_articles.txt"

echo "🔦 探照灯开始工作..."

# 1. 扫描所有 RSS feeds
echo "📡 扫描 RSS Feeds..."
blogwatcher scan 2>/dev/null > /dev/null

# 2. 获取最新文章列表
echo "📰 获取文章列表..."
blogwatcher articles 2>/dev/null | grep "\[new\]" | head -50 > "$ARTICLES_FILE"

# 3. 检查是否找到新文章
ARTICLE_COUNT=$(wc -l < "$ARTICLES_FILE" 2>/dev/null || echo 0)
echo "  找到 $ARTICLE_COUNT 篇新文章"

# 4. 生成内容发现 prompt
cat > "$CACHE_FILE" << 'PROMPT_END'
# 探照灯 · 今日发现

你是探照灯，一只专门照亮认知盲区的 AI。

## 你的使命
从以下文章列表中，找到最值得推荐的"认知盲区"内容——即 L（一个关注 AI/财经/科技的投资者）从未深度探索过、但一旦知道会大幅拓展认知边界的领域。

## 筛选标准（按重要性排序）
1. **跨学科连接** — 不同领域的思想碰撞（比如：生物学→经济学，物理学→心理学）
2. **反直觉发现** — 打破常识认知的内容
3. **历史中被遗忘的洞见** — 经典但今天少有人知道的思想
4. **新兴科学** — 刚刚出现的重要研究
5. **思维框架** — 能改变你看世界方式的方法论

## 筛选禁忌
- ❌ 不推荐他已经关注的话题（AI进展、A股、大模型动态）
- ❌ 不推荐过于技术细节的纯学术论文
- ❌ 不推荐过于明显/大众化的新闻

## 输出格式（必须严格遵循）
从列表中精选 2-3 篇，用以下格式呈现：

---
🔦 **[发现标题]**
来源：{博客/媒体}
链接：{URL}

**为什么你应该知道**（3-5句话）：
{解释这个发现在认知上的价值，以及它与你已知世界的联系}

**一个行动**：
{具体、可执行的"下一步"，比如"阅读某篇文章"、"搜索某个概念"等}
---

## 文章列表
PROMPT_END

cat "$ARTICLES_FILE" >> "$CACHE_FILE"

echo "✅ 探照灯发现完成: $CACHE_FILE"
echo "$ARTICLE_COUNT 篇文章待分析"
