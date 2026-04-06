#!/usr/bin/env bash
# gen_ai_news.sh - AI要闻日报数据采集
# 采集AI领域最新新闻，写入 /tmp/ai_daily_prompt.md，供后续生成报告使用

set -e
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.nvm/versions/node/v22.22.0/bin:/usr/bin/python3"

echo "正在采集AI要闻..."

# 搜索国际AI新闻
INTERNATIONAL=$(python3 -c "
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')
print(f'## 国际AI热点（搜索时间: {today}）')
" 2>/dev/null)

# 通过 curl 抓取 HackerNews AI 相关内容
HN_NEWS=$(curl -s --connect-timeout 5 "https://hn.algolia.com/api/v1/search?query=AI+artificial+intelligence&tags=story&hitsPerPage=8" 2>/dev/null | python3 -c "
import json, sys, datetime
try:
    data = json.load(sys.stdin)
    print('## 国际AI热点（来源: HackerNews）')
    for i, hit in enumerate(data.get('hits', [])[:8], 1):
        title = hit.get('title', '')
        url = hit.get('url', '')
        _tags = hit.get('_tags', [])
        if title and ('ai' in title.lower() or 'AI' in title):
            print(f'{i}. 【HackerNews】{title}')
            if url:
                print(f'   {url}')
except Exception as e:
    print(f'HackerNews API 获取失败: {e}')
" 2>/dev/null) || HN_NEWS=""

echo "$HN_NEWS"

# 搜索国内AI新闻（使用东方财富/新浪等公开接口）
echo ""
echo "## 中文AI热点（来源: 东方财富）"
curl -s --connect-timeout 8 "https://np-listapi.eastmoney.com/comm/web/getNPList?client=web&bPageSize=10&bPage=1&dtype=4&order=1&keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD" \
  -H "User-Agent: Mozilla/5.0" 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    items = data.get('data', {}).get('list', [])
    for i, item in enumerate(items[:5], 1):
        print(f'{i}. {item.get(\"title\", \"\")}')
        print(f'   {item.get(\"summary\", \"\")[:100]}')
except:
    print('获取失败')
" 2>/dev/null || echo "获取失败"

# ── 腾讯新闻AI精选 ─────────────────────────────────────────────
TN_CLI="$HOME/.openclaw/workspace/skills/tencent-news/tencent-news-cli"
if [ -f "$TN_CLI" ] && [ -f "$HOME/.config/tencent-news-cli/config.json" ]; then
    KEY=$(python3 -c "import json; d=json.load(open('$HOME/.config/tencent-news-cli/config.json')); print(d.get('TENCENT_NEWS_APIKEY',''))" 2>/dev/null)
    if [ -n "$KEY" ]; then
        export TENCENT_NEWS_APIKEY="$KEY"
        TN_AI=$("$TN_CLI" ai-daily 2>/dev/null)
        if [ -n "$TN_AI" ]; then
            echo ""
            echo "## 腾讯AI精选（tencent-news ai-daily）"
            echo "$TN_AI"
        fi
    fi
fi

# 输出汇总
echo ""
echo "---"
echo "✅ AI要闻采集完成"

