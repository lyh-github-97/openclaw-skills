---
name: daily-report-skill
description: 日报生成技能。定时触发或手动触发，采集数据、生成报告、发送到飞书。触发词：AI要闻、财经早报、财经晚报、A股盘前、探照灯、每日荐股、daily report、生成日报、盘前情报。当需要生成任何日报时激活。
---

# 日报生成技能

## 执行流程

收到任务后，根据 `report_type` 执行对应流程：
1. 采集数据（运行脚本或使用工具）
2. 生成报告正文
3. 发送报告
4. 回复「完成」

---

## report_type: ai-news（AI要闻日报，08:00）

### 采集
使用 `web_search` 搜索以下内容：
1. `AI artificial intelligence news March 2026`
2. `OpenAI Google DeepMind Anthropic March 2026`

### ⚠️ 安全规则
**如果 web_search 失败（fetch failed），绝对不能发送未经搜索验证的报告。**
处理方式（按优先级）：
1. 切换直连网络重试搜索
2. 如搜索仍失败，在报告顶部添加醒目警告（不能只放底部小字）：
   ```
   ⚠️ 网络搜索不可用，以下内容为AI基于公开知识的推断，未经实时验证，
   请以权威媒体为准。
   ```
3. 警告必须加在报告最顶部，字号醒目
4. **禁止在底部小字蒙混过关**

### 报告格式
```
🤖 AI要闻日报
📅 {日期}
⚠️ [如网络不可用则加此行]

🌎 国际AI热点
1. 【来源】标题
   → 摘要

🇨🇳 中文AI热点
1. 标题
   → 摘要

🤖 大厂动态
- ...

📡 机构观点
- ...
```

---

## report_type: market-morning（财经早报 + AI要闻，08:30）

> 整合了原来的 ai-daily-report（08:00，已合并），AI要闻 + 财经数据一站式推送。
> 工作日（周一到周五）发送，周末（周六周日）不发，改为 market-weekend 前瞻报告。
> **非交易日（非周末且非节假日）**：自动切换为周末前瞻模式，采集新闻和题材催化，不采集行情数据。

### 采集

**① 判断是否交易日**
运行：`bash /Users/liyaohua/.openclaw/skills/daily-report-skill/scripts/gen_market_report.sh morning`
- 若今日非交易日（周末/节假日），脚本自动切换为 `weekend` 模式，生成 `/tmp/market_weekend_prompt.md`
  → 走 market-weekend 流程
- 若今日为交易日，脚本正常生成 `/tmp/market_morning_prompt.md` → 继续下一步

**② 财经数据**
运行：`bash /Users/liyaohua/.openclaw/skills/daily-report-skill/scripts/gen_market_report.sh morning`
输出：`/tmp/market_morning_prompt.md`
包含：大盘指数（三源验证）、热门个股、热门板块

**③ AI要闻**
使用 `web_search` 搜索以下内容：
1. `AI artificial intelligence news March 2026`
2. `OpenAI Google DeepMind Anthropic March 2026`

### ⚠️ 安全规则
**如果 web_search 失败（fetch failed），绝对不能发送未经搜索验证的内容。**
处理方式：加顶部醒目警告，内容改为AI基于公开知识的推断，不可伪造实时数据。

### 生成报告
读取 `/tmp/market_morning_prompt.md`，结合自己的分析能力 + AI新闻，生成综合早报。

### 报告格式
```
📊 财商早报 | {日期}

🤖【AI要闻】（国际 + 国内AI热点，3-5条）
{AI新闻摘要}

📈【大盘数据】（三源验证）
{上证、深证、创业板、科创50、沪深300 实时行情}

🔥【热门个股】
{今日涨幅最大/成交最活跃的个股}

🔥【热门板块】
{今日表现最强的板块及主力资金流向}

📰【财经早参】
{大盘判断 + 市场数据 + 重点新闻解读}
```

---

## report_type: market-evening（财经晚报，16:00）

### 采集

**① 判断是否交易日**
运行：`bash /Users/liyaohua/.openclaw/skills/daily-report-skill/scripts/gen_market_report.sh evening`
- 若今日非交易日（周末/节假日），脚本自动切换为 `weekend` 模式，生成 `/tmp/market_weekend_prompt.md`
  → 走 market-weekend 流程
- 若今日为交易日，脚本正常生成 `/tmp/market_evening_prompt.md` → 继续下一步

**② 财经数据**
运行：`bash /Users/liyaohua/.openclaw/skills/daily-report-skill/scripts/gen_market_report.sh evening`
输出：`/tmp/market_evening_prompt.md`

### 追加板块机会（每日荐股）
调用 mx_select_stock API 获取今日热门板块和推荐股票：

```bash
curl -s -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/stock-screen' \
  -H 'Content-Type: application/json' \
  -H 'apikey: mkt_PJ-H2IsUhBPFK2tm_K31YE7eRFIlm7uR_E5wDELHg40' \
  -d '{"keyword":"今日涨幅前20热门股", "pageNo": 1, "pageSize": 10}'
```

将 API 返回结果追加到 `/tmp/market_evening_prompt.md` 末尾，作为【板块机会】参考数据。

### 生成报告
读取 `/tmp/market_evening_prompt.md`，结合自己的分析能力 + 板块机会数据，生成晚报。

### 报告格式
```
📊 财经晚报 | {日期}

【大盘收盘】
{收盘数据和分析}

【今日板块机会】  ← 新增板块荐股
{结合选股数据，精选2-3个有价值的板块/个股推荐}
{包含：板块名称、代表股票代码、推荐理由}

【重要资讯】
{今日重大财经新闻解读}
```

---

## report_type: market-weekend（周末前瞻，周六/周日）

> 周六周日 A股不开盘，不发行情数据，改为分析下周的热门题材催化。

### 采集
运行：`bash /Users/liyaohua/.openclaw/skills/daily-report-skill/scripts/gen_market_report.sh weekend`
输出：`/tmp/market_weekend_prompt.md`

### 生成报告
读取 `/tmp/market_weekend_prompt.md`，生成下周前瞻报告。

### 报告格式
```
📊 周末前瞻 | {日期}

【周末全球动态】
{美股、外盘商品、汇率等收盘情况，对A股开盘的指引}

【下周大盘前瞻】
{基于周末消息，判断下周大盘整体方向}

【重点催化题材】
{2-4个下周最有可能表现的主题，每个说明：催化剂 + 逻辑 + 代表股/板块}

【潜在风险】
{需要警惕的风险点：地缘、宏观数据、解禁等}

【操作计划参考】
{结合周末消息，下周盘前的主要思路}
```

---

## report_type: catalyst（A股盘前研报，07:30工作日）

### 采集
直接使用工具搜索（不需要运行脚本）：

使用 `web_search` 搜索以下9个主题，各取5-8条最新结果：
1. OpenAI GPT artificial intelligence March 2026
2. AI大模型 人工智能 2026年3月 最新
3. semiconductor芯片 半导体 最新消息
4. A股 市场 今日 操作建议
5. 美股 futures 纳斯达克 道琼斯
6. 黄金 原油 大宗商品
7. 人民币 汇率 USD/CNY
8. 政策 宏观 重要会议
9. 地缘政治 黑天鹅

### 生成报告
将所有搜索结果整理成盘前研报。

### 报告格式
```
📋 盘前情报 | {日期}

【外盘情绪】
{美股期货、黄金、原油}

【大盘判断】
{今日操作建议}

【重点板块】
{热门板块}
```

---

## report_type: spotlight（探照灯，10:00）

### 采集
运行：`bash /Users/liyaohua/.openclaw/skills/daily-report-skill/scripts/gen_spotlight.sh`
输出：`/tmp/spotlight_raw.md`

### 生成报告
读取 `/tmp/spotlight_raw.md`，根据其中的文章列表，精选2-3篇最有价值的文章进行推荐。严格遵循文件中的输出格式。

**⚠️ 重要：所有链接必须真实有效，禁止留"待补充"。**
如果某篇文章没有真实URL，删除该链接字段即可，不要写占位符。发送前自己检查一遍所有链接是否可访问。

保存为：`/tmp/spotlight_final.md`

---

## report_type: stock-pick（每日荐股，19:00）

### 采集
使用 `mx_select_stock` skill 的工具，筛选条件：
1. 今日涨幅较好的热门股
2. 低估值高增长潜力股
3. 近期热门板块的龙头股

### 生成报告
整理成荐股报告，包含：股票名称、代码、推荐理由、风险提示。

---

## 发送

### 发送到财财（飞书）
```bash
node /Users/liyaohua/.openclaw/skills/daily-report-skill/scripts/send_to_finance.js <报告文件路径>
```

### 发送到探照灯（飞书）
```bash
node /Users/liyaohua/.openclaw/skills/daily-report-skill/scripts/send_to_spotlight.js oc_62b0d7d187be614f8bdce954e5494358 <报告文件路径>
```

### 发送到 Telegram
使用 `message` 工具发送到 Telegram。

---

## 完成

所有报告发送成功后，只回复「完成」二字，不包含任何报告内容。

## 注意事项

- 脚本中 node 路径已硬编码：`/Users/liyaohua/.nvm/versions/node/v22.22.0/bin/node`
- 脚本中 python3 路径：`/usr/bin/python3`
- 如果脚本执行失败，尝试手动从命令行运行相同命令来调试
- 发送前检查报告文件是否为空（>100字节）
- 所有脚本都有完整 PATH 设置，cron 环境可正常运行
