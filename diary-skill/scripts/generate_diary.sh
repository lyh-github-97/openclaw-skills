#!/bin/bash
# 生成昨日日记并发送到财财飞书窗口（图片形式）
# 用法: bash generate_diary.sh [日期 YYYY-MM-DD]

set -e

# 设置 PATH（LaunchAgent 环境下没有 nvm）
export PATH="/Users/liyaohua/.nvm/versions/node/v22.22.0/bin:/usr/local/bin:/usr/bin:/bin:$HOME/.npm-global/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORY_DIR="$HOME/.openclaw/workspace/memory"
SKILL_DIR="$HOME/.openclaw/skills/diary-skill"
DIARY_IMAGE_SCRIPT="$SKILL_DIR/scripts/diary_image.py"
SEND_IMAGE_SCRIPT="$SKILL_DIR/scripts/send_diary_image.js"

# 获取日期（默认昨天）
if [ -n "$1" ]; then
    TARGET_DATE="$1"
else
    TARGET_DATE=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)
fi

MEMORY_FILE="$MEMORY_DIR/$TARGET_DATE.md"
DIARY_FILE="$MEMORY_DIR/diary-$TARGET_DATE.md"
DIARY_IMAGE_FILE="$MEMORY_DIR/diary-$TARGET_DATE.png"
LONGTERM_FILE="$MEMORY_DIR/../MEMORY.md"

echo "[diary] 生成 $TARGET_DATE 日记（图片模式）..."

# 检查记忆文件
if [ ! -f "$MEMORY_FILE" ]; then
    echo "[diary] 错误: 找不到记忆文件 $MEMORY_FILE"
    exit 1
fi

# 调用 MiniMax API 生成日记（Python 直接读文件，避免 bash 引号问题）
DIARY_CONTENT=$(TARGET_DATE="$TARGET_DATE" MEMORY_DIR="$MEMORY_DIR" python3 << 'PYEOF'
import subprocess, json, os, glob, sys

target_date = os.environ['TARGET_DATE']
memory_dir = os.environ['MEMORY_DIR']
memory_file = os.path.join(memory_dir, target_date + ".md")
longterm_file = os.path.join(memory_dir, "..", "MEMORY.md")

memory_content = open(memory_file).read()
longterm_content = open(longterm_file).read() if os.path.exists(longterm_file) else ""

prompt = f"""你是一只 AI 助手（名叫财财），正在为自己的主人（L）写私人日记。

## 昨日记忆（必须以此为准，不许编造）
{memory_content}

## 长期记忆摘要
{longterm_content}

## 绝对禁止
- 禁止凭空编造任何人物、项目、事件、决策
- 禁止写任何记忆中不存在的内容
- 禁止套用"通用AI助手反思模板"
- 你的每一个字都必须来自上面的记忆文件

## 写作要求
根据记忆文件，写一篇400-600字的日记：
1. 用第一人称"我"，站在财财的视角
2. 标题用 **今日最值得记住的一件事** / **重要决策和改动** / **新的学习和认知** / **做得不够好的地方** / **明天要做的事**
3. 每个板块必须至少写2-3句，言之有物
4. 日记里必须出现记忆文件中的具体项目名、人名、决策、结论
5. 如果记忆里有"待办"事项，明天要做的事必须对应承接
6. 不要写"我学到了很多"这种废话，要写具体学到了什么

标题格式：📅 日记 · {target_date}（单独一行）
然后是5个板块，标题 **加粗** 单独一行，下面是正文。

直接输出日记正文，不要加任何前言。"""

# Find API key
api_key = ''
for path in glob.glob(os.path.expanduser('~/.openclaw/agents/*/agent/auth-profiles.json')):
    try:
        d = json.load(open(path))
        for prof in d.get('profiles', {}).values():
            if isinstance(prof, dict) and prof.get('type') == 'api_key':
                key = prof.get('key', '')
                if key and key.startswith('sk-'):
                    api_key = key
                    break
        if api_key:
            break
    except:
        pass

if not api_key:
    print('ERROR: MINIMAX_API_KEY not found', file=sys.stderr)
    sys.exit(1)

payload = {
    'model': 'abab6.5s-chat',
    'messages': [
        {'role': 'system', 'content': '你是一只 AI 助手（名叫财财），正在为主人写私人日记。风格：真实、有想法、不套路。'},
        {'role': 'user', 'content': prompt}
    ],
    'temperature': 0.3,
    'max_tokens': 1500
}

proc = subprocess.run(
    ['curl', '-s', '--max-time', '60',
     '-H', 'Content-Type: application/json',
     '-H', f'Authorization: Bearer {api_key}',
     '-d', json.dumps(payload),
     'https://api.minimax.chat/v1/text/chatcompletion_v2'],
    capture_output=True
)
try:
    d = json.loads(proc.stdout)
    msg = d.get('choices', [{}])[0].get('message', {})
    content = msg.get('content', '') or msg.get('reasoning_content', '')
    if not content:
        print(f'ERROR: empty response. base_resp={d.get("base_resp")}', file=sys.stderr)
        sys.exit(1)
    print(content)
except Exception as e:
    print(f'Parse error: {e}', file=sys.stderr)
    print(f'Stdout: {proc.stdout[:500]}', file=sys.stderr)
    sys.exit(1)
PYEOF
)

if [ -z "$DIARY_CONTENT" ]; then
    echo "[diary] ❌ API 调用失败"
    exit 1
fi

# 保存日记文本
echo "$DIARY_CONTENT" > "$DIARY_FILE"
echo "[diary] 日记已保存: $DIARY_FILE"

# 生成图片
echo "[diary] 🎨 生成日记图片..."
python3 "$DIARY_IMAGE_SCRIPT" "$DIARY_FILE" "$DIARY_IMAGE_FILE" "$TARGET_DATE"
if [ ! -f "$DIARY_IMAGE_FILE" ]; then
    echo "[diary] ❌ 图片生成失败"
    exit 1
fi
echo "[diary] 图片已生成: $DIARY_IMAGE_FILE"

# 发送到财财飞书
echo "[diary] 📤 发送到财财..."
node "$SEND_IMAGE_SCRIPT" "$DIARY_IMAGE_FILE"
if [ $? -eq 0 ]; then
    echo "[diary] ✅ 发送成功"
else
    echo "[diary] ⚠️ 发送失败（图片已保存，可手动发送）"
fi
