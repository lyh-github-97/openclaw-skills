#!/bin/bash
# 财经早报/晚报数据采集
# 用法: gen_market_report.sh <morning|evening|weekend>
#        或不传参数：自动判断（根据时间和是否为交易日）
#
# 是否开盘判断逻辑：
#   1. 读取 ~/.openclaw/scripts/a_share_holidays.json 中的节假日列表
#   2. 若今天在列表中 → 非交易日，跳过
#   3. 若今天是周六/周日 → 非交易日，跳过
#   4. 其他情况 → 交易日，按时间出 morning/evening

export PATH="/Users/liyaohua/.nvm/versions/node/v22.22.0/bin:$HOME/.nvm/versions/node/v22.22.0/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/liyaohua"
export USER="liyaohua"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
REPORT_TYPE="${1:-}"

# ── 判断今天是否 A 股交易日 ────────────────────────────────────
is_trading_day() {
    local today
    today=$(date +%Y-%m-%d)

    # 周六周日直接跳过
    local dow
    dow=$(date +%u)  # 1=周一 ... 7=周日
    if [ "$dow" -ge 6 ]; then
        echo "[is_trading_day] 今天($today) 是周末，跳过"
        return 1
    fi

    # 查节假日表
    local holiday_file="$HOME/.openclaw/scripts/a_share_holidays.json"
    if [ -f "$holiday_file" ]; then
        local year
        year=$(date +%Y)
        local holidays
        # 用 python 解析 JSON，干净可靠
        holidays=$(python3 -c "
import json, sys
try:
    d = json.load(open('$holiday_file'))
    dates = d.get('$year', {}).get('holidays', [])
    today = '$today'
    if today in dates:
        print('HOLIDAY')
        sys.exit(0)
    else:
        print('TRADING')
        sys.exit(0)
except Exception as e:
    print('ERROR:' + str(e), file=sys.stderr)
    sys.exit(1)
" 2>/dev/null)

        case "$holidays" in
            HOLIDAY)
                echo "[is_trading_day] 今天($today) 是节假日，跳过"
                return 1
                ;;
            TRADING)
                echo "[is_trading_day] 今天($today) 是交易日"
                return 0
                ;;
            ERROR*)
                echo "[is_trading_day] ⚠️ 节假日表读取失败，默认跳过: $holidays"
                return 1
                ;;
            *)
                echo "[is_trading_day] ⚠️ 未知状态 '$holidays'，跳过"
                return 1
                ;;
        esac
    else
        echo "[is_trading_day] ⚠️ 节假日表不存在: $holiday_file，跳过"
        return 1
    fi
}

# ── 自动判断报告类型 ──────────────────────────────────────────
if [ -z "$REPORT_TYPE" ]; then
    HOUR=$(date +%H)
    if [ "$HOUR" -lt 12 ]; then
        REPORT_TYPE="morning"
    else
        REPORT_TYPE="evening"
    fi
    echo "[自动判断: $REPORT_TYPE ($(date '+%Y-%m-%d %H:%M'))]"
fi

# ── 判断是否发报告 ────────────────────────────────────────────
if ! is_trading_day; then
    echo "[$(date)] 今日非交易日，切换到周末前瞻模式..."
    REPORT_TYPE="weekend"
fi

if [ "$REPORT_TYPE" = "morning" ]; then
    OUTPUT_FILE="/tmp/market_morning_prompt.md"
elif [ "$REPORT_TYPE" = "evening" ]; then
    OUTPUT_FILE="/tmp/market_evening_prompt.md"
elif [ "$REPORT_TYPE" = "weekend" ]; then
    OUTPUT_FILE="/tmp/market_weekend_prompt.md"
else
    OUTPUT_FILE="/tmp/market_${REPORT_TYPE}_prompt.md"
fi

echo "[$(date)] 生成${REPORT_TYPE}财经报告数据..."

# ── 采集市场数据 ──────────────────────────────────────────────
python3 /Users/liyaohua/.openclaw/scripts/market_report.py "$REPORT_TYPE" 2>&1

# 移动输出文件
if [ -f "/tmp/morning_prompt.md" ]; then
    mv /tmp/morning_prompt.md "$OUTPUT_FILE"
    echo "✅ Prompt已生成: $OUTPUT_FILE"
elif [ -f "/tmp/evening_prompt.md" ]; then
    mv /tmp/evening_prompt.md "$OUTPUT_FILE"
    echo "✅ Prompt已生成: $OUTPUT_FILE"
elif [ -f "/tmp/weekend_prompt.md" ]; then
    mv /tmp/weekend_prompt.md "$OUTPUT_FILE"
    echo "✅ Prompt已生成: $OUTPUT_FILE"
elif [ -f "$OUTPUT_FILE" ]; then
    echo "✅ Prompt已生成: $OUTPUT_FILE"
else
    echo "⚠️ Prompt文件未找到"
fi

# ── 追加腾讯新闻热点（工作日）──────────────────────────────────
if [ "$REPORT_TYPE" != "weekend" ]; then
    echo "" >> "$OUTPUT_FILE"
    echo "## 【腾讯新闻热点】" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    TN_CLI="$HOME/.openclaw/workspace/skills/tencent-news/tencent-news-cli"
    if [ -f "$TN_CLI" ] && [ -f "$HOME/.config/tencent-news-cli/config.json" ]; then
        KEY=$(python3 -c "import json; d=json.load(open('$HOME/.config/tencent-news-cli/config.json')); print(d.get('TENCENT_NEWS_APIKEY',''))" 2>/dev/null)
        if [ -n "$KEY" ]; then
            export TENCENT_NEWS_APIKEY="$KEY"
            TN_OUTPUT=$("$TN_CLI" hot 2>/dev/null)
            if [ -n "$TN_OUTPUT" ]; then
                echo "$TN_OUTPUT" >> "$OUTPUT_FILE"
                echo "✅ 腾讯新闻热点已追加"
            else
                echo "⚠️ 腾讯新闻无输出"
            fi
        else
            echo "⚠️ 腾讯新闻API Key未找到"
        fi
    else
        echo "⚠️ 腾讯新闻CLI未安装，跳过"
    fi
fi
