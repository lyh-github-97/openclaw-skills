#!/bin/bash
# gen_and_send.sh - 豆包生图 + 下载 + 飞书发送（一键完成）
# 用法: ./gen_and_send.sh "图片描述" [发送给谁]
#   发送给谁: 默认 L 私聊 (ou_8e79daae8f22d612e09f7ffa41e12aae)
#
# 依赖: opencli, curl, message tool
# 注意: 需要先确保 opencli operate 连到豆包 AI 创作页

set -e

PROMPT="${1:-}"
TARGET="${2:-user:ou_8e79daae8f22d612e09f7ffa41e12aae}"
TMP_DIR="/tmp/ai_gen"
mkdir -p "$TMP_DIR"

if [ -z "$PROMPT" ]; then
    echo "用法: $0 <prompt描述> [飞书目标]"
    echo "示例: $0 \"一只赛博朋克机械猫\""
    exit 1
fi

TIMESTAMP=$(date +%s)
IMG_FILE="$TMP_DIR/gen_${TIMESTAMP}.jpg"

echo "🎨 开始生成: $PROMPT"

# ========== 步骤1: 打开豆包 AI 创作页 ==========
echo "📂 打开豆包 AI 创作页..."
opencli operate open "https://www.doubao.com/chat/create-image" 2>/dev/null
sleep 5

# ========== 步骤2: 输入 prompt ==========
echo "⌨️  输入 prompt..."
opencli operate type 2 "$PROMPT" 2>/dev/null

# ========== 步骤3: 点击生成 ==========
echo "▶️  点击生成..."
opencli operate click 53 2>/dev/null  # "图像生成" 按钮
echo "⏳ 等待生成（约25秒）..."
sleep 25

# ========== 步骤4: 提取图片 URL ==========
echo "🔍 提取图片 URL..."
RAW=$(opencli operate eval "JSON.stringify([...document.querySelectorAll('img[src*=rc_gen_image]')].map(i=>i.src).filter(s=>s.includes('jpeg')||s.includes('jpg')).slice(0,1))" 2>/dev/null)
URL=$(echo "$RAW" | grep -oE 'https://p[0-9]+-flow-imagex-sign\.byteimg\.com/[^"]+' | head -1)

if [ -z "$URL" ]; then
    echo "❌ 未找到图片 URL，原始: $RAW"
    exit 1
fi

echo "✅ 获取到 URL: ${URL:0:60}..."

# ========== 步骤5: 下载 ==========
echo "📥 下载图片..."
HTTP_CODE=$(curl -sL -o "$IMG_FILE" -w "%{http_code}" "$URL" --connect-timeout 10 --max-time 30)
if [ "$HTTP_CODE" != "200" ]; then
    echo "❌ 下载失败 (HTTP $HTTP_CODE)"
    exit 1
fi
SIZE=$(du -h "$IMG_FILE" | cut -f1)
echo "✅ 下载成功: $IMG_FILE ($SIZE)"

# ========== 步骤6: 发送飞书 ==========
echo "📤 发送到飞书..."

# 记录文件路径（供后续处理）
echo "FILE:$IMG_FILE" > /tmp/last_gen_file.txt
echo ""
echo "========================================"
echo "✅ 完成！"
echo "📁 文件: $IMG_FILE"
echo "👤 目标: $TARGET"
echo ""
echo "下一步：用 message 工具发送："
echo "  message(action=send, channel=feishu, target=\"$TARGET\", media=\"$IMG_FILE\", message=\"🐱 $PROMPT\")"
echo "========================================"
