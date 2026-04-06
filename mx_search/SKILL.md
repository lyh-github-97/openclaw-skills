---
name: mx_search
description: 妙想资讯搜索 - 基于东方财富妙想搜索能力获取金融资讯
---

# 妙想资讯搜索 (mx_search)

基于东方财富妙想搜索能力获取金融资讯，用于获取涉及时效性信息或特定事件信息的任务，包括新闻、公告、研报、政策、交易规则、具体事件等。

## 功能

- 个股资讯搜索（研报、观点、新闻）
- 板块/主题搜索（行业新闻、政策解读）
- 宏观/风险分析
- 综合解读（大盘异动、资金流向等）

## 使用方式

### 环境变量

将 API Key 存到环境变量：
```
MX_APIKEY=mkt_PJ-H2IsUhBPFK2tm_K31YE7eRFIlm7uR_E5wDELHg40
```

### API 调用

```bash
curl -X POST 'https://mkapi2.dfcfs.com/finskillshub/api/claw/news-search' \
  -H 'Content-Type: application/json' \
  -H 'apikey: mkt_PJ-H2IsUhBPFK2tm_K31YE7eRFIlm7uR_E5wDELHg40' \
  -d '{"query":"查询内容"}'
```

### 问句示例

| 类型 | 示例 |
|------|------|
| 个股资讯 | 格力电器最新研报、贵州茅台机构观点 |
| 板块/主题 | 商业航天板块近期新闻、新能源政策解读 |
| 宏观/风险 | A股具备自然对冲优势的公司 汇率风险、美联储加息对A股影响 |
| 综合解读 | 今日大盘异动原因、北向资金流向解读 |

## 返回字段

| 字段 | 释义 |
|------|------|
| title | 信息标题 |
| secuList | 关联证券列表 |
| trunk | 信息核心正文 |

## 注意事项

- 每天免费 50 次
- 避免搜索非权威或过时的金融信息
