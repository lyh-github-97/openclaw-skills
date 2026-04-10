---
name: spotlight-daily
description: >
  探照灯资讯精选。每日 10:00 执行。
  读取 /tmp/spotlight_articles.txt，从今日文章中精选2-3篇最具认知价值的，
  生成结构化报告并发送给李耀华。
---

# 探照灯资讯精选

## 执行步骤

### 1. 读取文章列表
```bash
cat /tmp/spotlight_articles.txt
```
如果文件不存在或为空，回复「今日无新文章」。

### 2. 生成报告
格式：
```
🔦 [标题]
来源：[来源]
URL：[链接]
为什么你应该知道：[3-5句核心内容]
行动建议：[一句话]

---
🔦 [第二篇...]

---
🔦 [第三篇...]
```

### 3. 保存报告
将报告内容保存到 /tmp/spotlight_final.md

### 4. 发送（用脚本，不走 message 工具）
运行以下命令发送报告：
```
node /Users/liyaohua/.openclaw/scripts/spotlight_send.js oc_62b0d7d187be614f8bdce954e5494358 /tmp/spotlight_final.md
```
如果脚本输出包含"发送成功"，回复「完成」。

## 注意事项

- 精选最有认知价值的2-3篇，不要堆砌
- 每篇要有实质性内容，不是标题摘要
- 没有好文章时，直接说「今日无值得推荐的」
