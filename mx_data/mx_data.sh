#!/bin/bash
# 妙想金融数据查询脚本

API_KEY="mkt_PJ-H2IsUhBPFK2tm_K31YE7eRFIlm7uR_E5wDELHg40"
API_URL="https://mkapi2.dfcfs.com/finskillshub/api/claw/query"

# 检查参数
if [ -z "$1" ]; then
    echo "用法: mx_data.sh \"查询内容\""
    echo "示例: mx_data.sh \"东方财富最新价\""
    echo "       mx_data.sh \"宁德时代PE\""
    echo "       mx_data.sh \"茅台vs五粮液财务对比\""
    exit 1
fi

QUERY="$1"

# 调用 API
response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -H "apikey: $API_KEY" \
    -d "{\"toolQuery\":\"$QUERY\"}")

# 输出结果
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
