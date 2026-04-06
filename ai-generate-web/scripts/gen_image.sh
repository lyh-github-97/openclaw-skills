#!/bin/bash
# gen_image.sh - 豆包AI创作页文生图
# 用法: ./gen_image.sh "图片描述" [保存路径]
# 输出: 下载完成后打印 FILE:<路径>
set -e

PROMPT="${1:-}"
SAVE_AS="${2:-}"
TMP_DIR="/tmp/ai_gen"
mkdir -p "$TMP_DIR"

if [ -z "$PROMPT" ]; then
    echo "用法: $0 <prompt> [保存路径]"
    exit 1
fi

TIMESTAMP=$(date +%s)
SAVE_AS="${SAVE_AS:-$TMP_DIR/gen_${TIMESTAMP}.jpg}"

echo "🎨 正在生成: $PROMPT"

# 打开 AI 创作页
opencli operate open "https://www.doubao.com/chat/create-image" 2>/dev/null
sleep 3

# 输入 prompt
opencli operate type 2 "$PROMPT" 2>/dev/null

# 点击生成按钮
opencli operate click 64 2>/dev/null
echo "⏳ 等待生成（约25秒）..."
sleep 25

# 提取图片 URL
RAW=$(opencli operate eval "JSON.stringify([...document.querySelectorAll('img[src*=rc_gen_image]')].map(i=>i.src))" 2>/dev/null)
URL=$(echo "$RAW" | grep -oE 'https://p[0-9]+-flow-imagex-sign\.byteimg\.com/[^"]+' | head -1)

if [ -z "$URL" ]; then
    echo "❌ 未找到图片 URL"
    echo "原始: $RAW"
    exit 1
fi

echo "📡 获取到 URL，开始下载..."

# 下载
HTTP_CODE=$(curl -sL -o "$SAVE_AS" -w "%{http_code}" "$URL" --connect-timeout 10 --max-time 30)
if [ "$HTTP_CODE" = "200" ]; then
    SIZE=$(du -h "$SAVE_AS" | cut -f1)
    echo "✅ 下载成功: $SAVE_AS ($SIZE)"
    echo "FILE:$SAVE_AS"
else
    echo "❌ 下载失败 (HTTP $HTTP_CODE)"
    exit 1
fi
