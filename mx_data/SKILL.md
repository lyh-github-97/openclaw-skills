---
name: mx_data
description: 妙想金融数据 - 基于东方财富权威数据库查询金融数据
---

# 妙想金融数据 (mx_data)

基于东方财富权威数据库及最新行情底层数据构建，支持通过自然语言查询金融相关数据。

## 功能

### 1. 行情类数据
- 股票、行业、板块、指数、基金、债券的实时行情
- 主力资金流向、估值等数据

### 2. 财务类数据
- 上市公司基本信息
- 财务指标（PE、PB、ROE等）
- 高管信息、主营业务、股东结构
- 融资情况

### 3. 关系与经营类数据
- 股票、非上市公司、股东及高管之间的关联关系
- 企业经营相关数据

## 使用方式

### API 调用

```bash
curl -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/query' \
  -H 'Content-Type: application/json' \
  -H 'apikey: mkt_PJ-H2IsUhBPFK2tm_K31YE7eRFIlm7uR_E5wDELHg40' \
  -d '{"toolQuery":"查询内容"}'
```

### 查询示例

| 类型 | 示例 |
|------|------|
| 个股行情 | 东方财富最新价、贵州茅台市值 |
| 财务指标 | 宁德时代PE、比亚迪ROE |
| 资金流向 | 今日北向资金流向 |
| 对比 | 茅台vs五粮液财务对比 |

## 返回字段说明

| 字段 | 释义 |
|------|------|
| data.dataTableDTOList | 标准化证券指标数据列表 |
| dataTableDTOList[].code | 证券代码（如 300059.SZ） |
| dataTableDTOList[].entityName | 证券全称 |
| dataTableDTOList[].table | 表格数据 |
| dataTableDTOList[].nameMap | 列名映射 |

## 注意事项

- 避免查询大数据范围（如3年每日行情），可能导致返回内容过多
- 每天免费 50 次
- 可避免模型基于过时知识回答金融问题
