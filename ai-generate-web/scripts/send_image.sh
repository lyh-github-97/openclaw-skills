#!/bin/bash
# send_image.sh - 豆包生图 + 飞书发送（一体化脚本）
# 用法: ./send_image.sh "图片描述" <user_id|chat_id> [feishu|local|both]
#   user_id: 私聊 open_id (ou_xxx)
#   chat_id: 群聊 id (oc_xxx)，传入时加 prefix: "chat:oc_xxx"
# 示例:
#   ./send_image.sh "一只赛博朋克机械猫" "ou_ee46528a780a35d08862c4374a261503"
#   ./send_image.sh "火车图" "chat:oc_4a496d6e2a0de23ca9e49a9493bb9522"

set -e

PROMPT="${1:-}"
TARGET="${2:-}"
MODE="${3:-feishu}"
TMP_DIR="/tmp/ai_gen"
TIMESTAMP=$(date +%s)

if [ -z "$PROMPT" ] || [ -z "$TARGET" ]; then
    echo "用法: $0 <prompt> <user_id|chat_id> [feishu|local|both]"
    echo "示例: $0 \"一只赛博朋克机械猫\" \"ou_ee46528a780a35d08862c4374a261503\""
    exit 1
fi

mkdir -p "$TMP_DIR"
OUTPUT_FILE="$TMP_DIR/gen_${TIMESTAMP}.jpg"

echo "🎨 [$TIMESTAMP] 开始生成图片..."
echo "   描述: $PROMPT"
echo "   目标: $TARGET"

# ===== 用 browser 工具打开豆包图像生成页 =====
# 注意：此脚本需要配合 OpenClaw browser 工具使用
# 在 OpenClaw 对话中，请用 browser 工具打开: https://www.doubao.com/chat/create-image
# 然后手动输入以下 ref编号（从快照中获取）:
# ref=文本框 → 输入 prompt
# ref=生成按钮 → 点击生成

# ===== 以下为备用方案：opencli operate =====
opencli operate open "https://www.doubao.com/chat/create-image" 2>/dev/null || true
sleep 3

# 获取快照找到输入框和按钮
STATE=$(opencli operate state 2>/dev/null || echo "")
echo "📋 等待 UI 加载..."

# 尝试输入（index 可能变化，以快照为准）
opencli operate type 2 "$PROMPT" 2>/dev/null && echo "✅ 已输入 prompt" || echo "⚠️ type 失败，尝试其他方式"

# 点击生成
opencli operate click 64 2>/dev/null && echo "✅ 已点击生成" || echo "⚠️ click 失败"

echo "⏳ 等待生成（约30秒）..."
sleep 30

# 提取图片 URL
RAW=$(opencli operate eval "JSON.stringify([...document.querySelectorAll('img[src*=rc_gen_image]')].map(i=>i.src))" 2>/dev/null || echo "[]")
URLS=$(echo "$RAW" | grep -oE 'https://p[0-9]+-flow-imagex-sign\.byteimg\.com/[^"]+' | head -4 || true)

if [ -z "$URLS" ]; then
    echo "❌ 未找到图片 URL"
    echo "   原始: $RAW"
    exit 1
fi

URL=$(echo "$URLS" | head -1)
echo "📡 获取到 URL: ${URL:0:60}..."

# 下载
HTTP_CODE=$(curl -sL -o "$OUTPUT_FILE" -w "%{http_code}" "$URL" --connect-timeout 15 --max-time 60 --user-agent "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
if [ "$HTTP_CODE" != "200" ]; then
    echo "❌ 下载失败 (HTTP $HTTP_CODE)"
    exit 1
fi

SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
echo "✅ 下载成功: $OUTPUT_FILE ($SIZE)"

# ===== 发送飞书 =====
if [ "$MODE" = "feishu" ] || [ "$MODE" = "both" ]; then
    echo "📤 发送到飞书..."

    # 判断是 user 还是 chat
    if [[ "$TARGET" == chat:* ]]; then
        CHAT_ID="${TARGET#chat:}"
        lark-cli im +messages-send --image "$OUTPUT_FILE" --chat-id "$CHAT_ID" --msg-type image 2>&1
    else
        lark-cli im +messages-send --image "$OUTPUT_FILE" --user-id "$TARGET" --msg-type image 2>&1
    fi

    if [ $? -eq 0 ]; then
        echo "✅ 飞书发送成功"
    else
        echo "❌ 飞书发送失败（图片已保存到 $OUTPUT_FILE）"
    fi
fi

if [ "$MODE" = "local" ] || [ "$MODE" = "both" ]; then
    echo "📁 本地保存: $OUTPUT_FILE"
fi

echo ""
echo "🎉 完成！"
echo "FILE:$OUTPUT_FILE"
