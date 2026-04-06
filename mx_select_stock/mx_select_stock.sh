#!/bin/bash
# 妙想智能选股脚本

API_KEY="mkt_PJ-H2IsUhBPFK2tm_K31YE7eRFIlm7uR_E5wDELHg40"
API_URL="https://mkapi2.dfcfs.com/finskillshub/api/claw/stock-screen"

# 检查参数
if [ -z "$1" ]; then
    echo "用法: mx_select_stock.sh \"选股条件\" [页码] [每页数量]"
    echo "示例: mx_select_stock.sh \"今日涨幅2%的股票\""
    echo "       mx_select_stock.sh \"PE低于20的股票\" 1 20"
    exit 1
fi

QUERY="$1"
PAGE=${2:-1}
SIZE=${3:-20}

# 调用 API
response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -H "apikey: $API_KEY" \
    -d "{\"keyword\":\"$QUERY\", \"pageNo\": $PAGE, \"pageSize\": $SIZE}")

# 输出结果
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
