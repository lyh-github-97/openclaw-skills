---
name: mx_select_stock
description: 妙想智能选股 - 基于条件筛选股票
---

# 妙想智能选股 (mx_select_stock)

基于股票选股条件（如行情指标、财务指标等），筛选满足条件的股票。

## 功能

- **条件选股**：按估值、盈利、技术形态筛选
- **行业/板块选股**：查询指定行业/板块内的股票
- **板块成分股**：查询板块指数的成分股
- **股票推荐**：股票、上市公司、板块/指数推荐
- **市场**：支持 A股、港股、美股

## 使用方式

### API 调用

```bash
curl -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/stock-screen' \
  -H 'Content-Type: application/json' \
  -H 'apikey: mkt_PJ-H2IsUhBPFK2tm_K31YE7eRFIlm7uR_E5wDELHg40' \
  -d '{"keyword":"选股条件", "pageNo": 1, "pageSize": 20}'
```

### 查询示例

| 类型 | 示例 |
|------|------|
| 涨幅选股 | 今日涨幅2%的股票 |
| 估值选股 | PE低于20的股票 |
| 行业选股 | 新能源板块股票 |
| 综合 | 净利润增长50%的消费股 |

## 返回字段说明

| 字段 | 释义 |
|------|------|
| data.result.total | 符合条件的股票数量 |
| data.result.columns | 表格列定义 |
| data.result.dataList | 股票数据列表 |
| responseConditionList | 筛选条件统计 |

## 注意事项

- 避免查询结果过多导致上下文爆炸
- 每天免费 50 次
- 可避免大模型使用过时信息选股
