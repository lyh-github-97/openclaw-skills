#!/bin/bash
# ai_gen_image.sh - 豆包文生图 + 飞书发送
# 触发词: "画一只" / "生成图片" / "生图"
# 用法: ./ai_gen_image.sh "橘猫" [发送目标]
#   发送目标: feishu(默认) | local | both

set -e

PROMPT="${1:-}"
OUTPUT_MODE="${2:-feishu}"
OUTPUT_DIR="/tmp/ai_gen"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

if [ -z "$PROMPT" ]; then
    echo "用法: $0 <prompt> [feishu|local|both]"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
RESULT_FILE="$OUTPUT_DIR/gen_result_${TIMESTAMP}.txt"

echo "🎨 [$TIMESTAMP] 豆包生图中... prompt=$PROMPT" | tee "$RESULT_FILE"

# 调用豆包
RAW_OUTPUT=$(opencli doubao ask "画一只$PROMPT" 2>/dev/null)

# 提取图片URL
IMAGE_URLS=$(echo "$RAW_OUTPUT" | grep -oE 'https://p[0-9]+-flow-imagex-sign\.byteimg\.com/[^[:space:]]+\.(jpg|jpeg|png|webp)(~[^[:space:]]+)?' | head -4 || true)

if [ -z "$IMAGE_URLS" ]; then
    echo "❌ 豆包未返回图片，可能当前上下文不支持" | tee -a "$RESULT_FILE"
    echo "原始: $RAW_OUTPUT" | head -5 >> "$RESULT_FILE"
    exit 1
fi

COUNT=$(echo "$IMAGE_URLS" | wc -l | tr -d ' ')
echo "✅ 获取 $COUNT 张图片" | tee -a "$RESULT_FILE"

# 下载
declare -a FILES=()
i=0
while IFS= read -r URL; do
    i=$((i + 1))
    F="$OUTPUT_DIR/gen_${TIMESTAMP}_${i}.jpg"
    HTTP_CODE=$(curl -sL -o "$F" -w "%{http_code}" "$URL" --connect-timeout 10 --max-time 30 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ]; then
        FILES+=("$F")
        echo "   ✅ [$i] $(basename $F)" | tee -a "$RESULT_FILE"
    else
        echo "   ❌ [$i] HTTP $HTTP_CODE" | tee -a "$RESULT_FILE"
    fi
done <<< "$IMAGE_URLS"

if [ ${#FILES[@]} -eq 0 ]; then
    echo "❌ 所有图片下载失败" | tee -a "$RESULT_FILE"
    exit 1
fi

echo ""
echo "📦 生成完成: ${#FILES[@]} 张图片"
echo "📁 保存于: $OUTPUT_DIR/"

# 返回文件列表供后续处理
for f in "${FILES[@]}"; do
    echo "FILE:$f"
done >> "$RESULT_FILE"

exit 0
