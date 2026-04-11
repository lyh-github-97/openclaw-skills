---
name: portfolio-tracker
description: A股持仓追踪与操作建议技能。每个交易日收盘后，主动询问用户持仓情况（股票代码、名称、成本价、股数），用户回答后更新持仓数据并进行深度分析，给出明确操作建议。触发词：持仓、持仓更新、成本、仓位、持仓建议。
---

# Portfolio Tracker - 持仓追踪技能

## 工作流程

### Step 1: 收盘后询问（triggered by cron or user）

每个交易日下午16:30后，检查今日是否为交易日（读取 memory/YYYY-MM-DD.md 确认开盘状态），然后向用户发送持仓询问：

```
📊 收盘了，请告诉我今天的持仓情况：
格式：股票代码|名称|成本价|股数
示例：000818|航锦科技|21.78|100
如无变化，回复"无变化"即可
```

### Step 2: 解析用户回复

用户可能回复：
- `无变化` → 读取现有 portfolio.json，跳过更新
- `000818|航锦科技|21.78|100` → 调用 update 更新
- 多只：`000818|航锦科技|21.78|100;002407|多氟多|28.53|200`
- 只想更新某只：`000818|21.78|100`（名称可省略）

### Step 3: 获取实时价格

使用工具获取持仓股实时/收盘价：
```bash
python3 ~/.openclaw/workspace-research/tools/get_stock_price.py 000818
python3 ~/.openclaw/workspace-research/tools/get_stock_price.py 002407
# 逐一获取每只持仓股价格
```

### Step 4: 计算浮亏并分析

计算每个持仓：
- 浮亏金额 = (现价 - 成本价) × 股数
- 浮亏比例 = (现价 - 成本价) / 成本价 × 100%
- 市值 = 现价 × 股数

### Step 5: 深度分析（参考 references/analysis_framework.md）

分析维度：
1. **浮亏/浮盈分析** — 所处区间，决定操作紧迫性
2. **仓位分析** — 占比是否过高
3. **消息面** — 是否有黑天鹅（立案、业绩预亏等）
4. **技术面** — 支撑位、趋势方向
5. **催化逻辑** — 持仓理由是否还存在

### Step 6: 输出分析报告

```
📊 持仓分析报告 [日期]

| 股票 | 成本 | 现价 | 涨跌 | 股数 | 浮亏 | 仓位占比 |
|------|------|------|------|------|------|----------|
| 航锦科技 | 21.78 | 15.62 | -26.4% | 100 | -616 | 10% |
| 多氟多 | 28.53 | 27.39 | -4.0% | 200 | -228 | 20% |

**深度分析：**
[个股逐个分析，逻辑清晰，结论明确]

**综合操作建议：**
1. 航锦科技：止损离场（立案调查未结束）
2. 多氟多：持有（逻辑未破，等待反弹）
```

## 关键规则

1. **数据优先**：持仓回答后，必须先用工具获取实时价格，再做分析
2. **结论明确**：每个持仓给出"买入/持有/卖出/止损"操作建议，不说"可能"
3. **分层表达**：先给结论，再给理由，最后给目标价
4. **止损严格**：立案调查、业绩造假等黑天鹅，优先建议止损
5. **不抄底**：跌停板不抄底，等开板换手充分后再判断

## 脚本接口

```bash
# 查看当前持仓
python3 ~/.openclaw/skills/portfolio-tracker/scripts/portfolio_manager.py show

# 更新单只持仓
python3 ~/.openclaw/skills/portfolio-tracker/scripts/portfolio_manager.py update 000818 航锦科技 21.78 100

# 删除持仓
python3 ~/.openclaw/skills/portfolio-tracker/scripts/portfolio_manager.py remove 000818

# JSON格式查看
python3 ~/.openclaw/skills/portfolio-tracker/scripts/portfolio_manager.py get
```

## 持仓文件路径

`~/.openclaw/workspace-research/catalyst_scanner/portfolio.json`

## 分析框架参考

详细分析维度见 `references/analysis_framework.md`
