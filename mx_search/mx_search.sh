#!/bin/bash
# 妙想资讯搜索脚本

API_KEY="mkt_PJ-H2IsUhBPFK2tm_K31YE7eRFIlm7uR_E5wDELHg40"
API_URL="https://mkapi2.dfcfs.com/finskillshub/api/claw/news-search"

# 检查参数
if [ -z "$1" ]; then
    echo "用法: mx_search.sh \"查询内容\""
    echo "示例: mx_search.sh \"立讯精密的资讯\""
    exit 1
fi

QUERY="$1"

# 调用 API
response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -H "apikey: $API_KEY" \
    -d "{\"query\":\"$QUERY\"}")

# 输出结果
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
