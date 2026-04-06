---
name: time-utils
version: 1.0.0
description: 时间感知工具集，提供交易日判断、当前交易时段、标准时间戳等功能。所有报告和决策必须优先调用此工具获取准确时间信息。
---

# Time Utils ⏰

## 核心功能

### 1. 交易日判断
- `is_trading_day(date=None, exchange="SSE")`
- 判断 A 股是否交易日（SSE/SZSE/HKEX/NYSE/NASDAQ）
- 优先用 akshare 精确日历，备用中国节假日粗略判断

### 2. 当前交易时段
- `current_session()`
- 返回：`pre_market` / `morning` / `lunch` / `afternoon` / `after_hours` / `closed` / `non_trading_day`

### 3. 市场状态（中文）
- `market_status()`
- 返回当前中文描述，如 "📈 早盘（09:30-12:00）"

### 4. 标准时间戳
- `report_timestamp()`
- 报告标准时间格式：`YYYY-MM-DD (周X) HH:MM:SS [交易日/非交易日] [时段]`
- **所有报告生成时必须调用此函数**，确保时间标注规范

### 5. 日期字符串
- `today_str()` → `YYYY-MM-DD`
- `now_str()` → `YYYY-MM-DD HH:MM:SS`

### 6. 下次开盘时间
- `next_open_time()`

## 使用规范

### 报告时间标注
```
【生成时间】
调用 time_utils.report_timestamp()
输出示例：2026-03-31 (周二) 16:05:00 [交易日] 📉 下午盘（13:00-15:00）
```

### Cron 执行前检查
在生成任何日报告前，先调用 `is_trading_day()`：
- 返回 False（非交易日）→ 直接退出，不生成报告
- 返回 True（交易日）→ 继续生成报告

### 日记日期归属
00:00 归属由工具层判断，不靠模型猜测：
- 00:00-00:59 → 判断为"今天"还是"昨天"由 `report_timestamp()` 自动处理

## 脚本路径
`/Users/liyaohua/.openclaw/skills/time-utils/scripts/time_utils.py`

## 快捷命令
```bash
python3 time_utils.py status  # 查看完整时间状态
python3 time_utils.py is_trading  # 今日是否交易
python3 time_utils.py session  # 当前时段
python3 time_utils.py timestamp  # 标准时间戳
python3 time_utils.py today  # 日期字符串
```
