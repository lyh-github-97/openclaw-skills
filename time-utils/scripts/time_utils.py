#!/usr/bin/env python3
"""
time_utils.py - 时间感知工具
提供交易日判断、当前时段、时间格式化等功能
"""
import datetime, json, subprocess, os

CACHE_DIR = "/tmp/time_utils_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# ========== 核心工具 ==========

def is_trading_day(date=None, exchange="SSE"):
    """
    判断是否为 A 股交易日
    date: datetime.date 或 str(YYYY-MM-DD)，默认今天
    exchange: SSE（上交所）/ SZSE（深交所）/ HKEX / NYSE / NASDAQ
    """
    if date is None:
        date = datetime.date.today()
    elif isinstance(date, str):
        date = datetime.date.fromisoformat(date)

    # 周末快速判断（国内交易所）
    if exchange in ("SSE", "SZSE"):
        if date.weekday() >= 5:  # 周六/周日
            return False

    # 尝试 akshare 获取精确日历
    try:
        import sys
        sys.path.insert(0, "/Users/liyaohua/.openclaw/skills/time-utils/scripts")
        result = subprocess.run(
            ["python3", "-c",
             f"import akshare as ak; cal=ak.tool_trade_date_hist_sina(); print(date.strftime('%Y-%m-%d') in cal['trade_date'].values)"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return "True" in result.stdout.strip()
    except Exception:
        pass

    # 备用：中国法定节假日粗略判断
    if _is_known_holiday(date, exchange):
        return False
    return True


def _is_known_holiday(date, exchange):
    """粗略节假日判断（已知的固定区间）"""
    if exchange not in ("SSE", "SZSE"):
        return False
    year = date.year
    # 元旦（1月1日）
    if date.month == 1 and date.day == 1:
        return True
    # 清明节假期（4月4-6日，A股休市）
    if date.month == 4 and date.day in (4, 5, 6):
        return True
    # 劳动节假期（5月1-5日）
    if date.month == 5 and date.day in (1, 2, 3, 4, 5):
        return True
    # 国庆节假期（10月1-7日）
    if date.month == 10 and date.day in (1, 2, 3, 4, 5, 6, 7):
        return True
    # 春节期间（腊月廿九～正月初七，简化判断）
    # 具体日期每年不同，保留作为兜底
    return False


def current_session(date=None):
    """
    返回当前属于哪个交易时段
    返回: pre_market / morning / lunch / afternoon / after_hours / closed / non_trading_day
    """
    if date is None:
        now = datetime.datetime.now()
    else:
        now = datetime.datetime.combine(date, datetime.time())

    # 非交易日
    if not is_trading_day(now.date()):
        return "non_trading_day"

    t = now.time()
    h, m = t.hour, t.minute

    if h < 9 or (h == 9 and m < 30):
        return "pre_market"
    elif h == 9 and m >= 30 or (h >= 10 and h < 12):
        return "morning"
    elif h >= 12 and h < 13:
        return "lunch"
    elif h >= 13 and h < 15:
        return "afternoon"
    elif h >= 15 and h < 20:
        return "after_hours"
    else:
        return "closed"


def next_open_time():
    """返回下一个 A 股开盘时间（datetime）"""
    now = datetime.datetime.now()
    today = now.date()

    # 尝试找下一个交易日
    for offset in range(8):
        check_date = today + datetime.timedelta(days=offset)
        if is_trading_day(check_date):
            open_time = datetime.datetime.combine(
                check_date, datetime.time(9, 30)
            )
            if open_time > now:
                return open_time
            # 今天已过，次日开盘
    return None


def market_status():
    """
    返回当前市场状态（中文描述）
    """
    session = current_session()
    status_map = {
        "pre_market": "📊 盘前（09:00-09:30）",
        "morning": "📈 早盘（09:30-12:00）",
        "lunch": "🍜 午间休市（12:00-13:00）",
        "afternoon": "📉 下午盘（13:00-15:00）",
        "after_hours": "📋 盘后（15:00-20:00）",
        "closed": "🌙 已休市（20:00-次日09:00）",
        "non_trading_day": "🚫 非交易日",
    }
    return status_map.get(session, "未知")


def now_str():
    """返回规范化的时间字符串（用于报告标注）"""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    """返回规范化日期字符串（YYYY-MM-DD）"""
    return datetime.date.today().isoformat()


def report_timestamp():
    """
    返回报告用的标准时间戳，包含交易日信息
    格式：YYYY-MM-DD (周X) HH:MM [交易日/非交易日] [时段]
    """
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()]
    time_str = now.strftime("%H:%M:%S")
    session = current_session()
    status = market_status()
    trading = "" if is_trading_day() else " [非交易日]"
    return f"{date_str} ({weekday}) {time_str}{trading} {status}"


# ========== 快捷脚本入口 ==========

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "status":
        print(f"📅 {report_timestamp()}")
        print(f"🕐 系统时间: {now_str()}")
        print(f"📊 市场状态: {market_status()}")
        print(f"🔍 今日是否为交易日: {'是' if is_trading_day() else '否'}")
        print(f"⏰ 下次开盘: {next_open_time()}")
        print(f"📝 日期字符串: {today_str()}")

    elif cmd == "is_trading":
        d = sys.argv[2] if len(sys.argv) > 2 else None
        if d:
            result = is_trading_day(datetime.date.fromisoformat(d))
        else:
            result = is_trading_day()
        print("是" if result else "否")

    elif cmd == "session":
        print(current_session())

    elif cmd == "timestamp":
        print(report_timestamp())

    elif cmd == "today":
        print(today_str())

    elif cmd == "weekday":
        print(["周一","周二","周三","周四","周五","周六","周日"][datetime.date.today().weekday()])
