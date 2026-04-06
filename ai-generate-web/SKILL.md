# ai-generate-web Skill

通过豆包网页端实现文生图，绕过 MiniMax 套餐不支持生图的限制。

---

## 生图方式一（首选）：opencli-rs jimeng

**命令行直接调用即梦，不占用浏览器，完全独立。**

```bash
opencli-rs jimeng generate "一只赛博朋克风格的机械猫"
```

**返回结果示例：**
```
| status | prompt | image_count | image_urls |
| success | 一只赛博朋克风格的机械猫 | 4 | https://p26-dreamina-sign... |
```

**下载并发送飞书：**
```bash
# 下载（复制返回的第一个 URL）
curl -sL -o /tmp/gen.webp "URL" --max-time 30

# 发送到飞书
python3 ~/.openclaw/scripts/send_image_as_zuoba.py /tmp/gen.webp
```

---

## 生图方式二（备选）：opencli doubao

**当方式一失败时使用。**

**提取图片 URL：**
返回内容中找到 `https://p*-flow-imagex-sign.byteimg.com/...` 格式的 URL，复制下来。

**下载并发送到飞书（两种方式）：**

方式 A — **Python 脚本（100% 稳定，推荐）：**
```bash
# 下载
curl -sL -o /tmp/gen.jpg "图片URL" --max-time 30

# 发送到飞书（选对应 agent 的脚本）
python3 ~/.openclaw/scripts/send_image_as_zuoba.py /tmp/gen.jpg          # 爪巴 → L 私聊
python3 ~/.openclaw/scripts/send_image_as_writer.py /tmp/gen.jpg        # 写写
python3 ~/.openclaw/scripts/send_image_as_spotlight.py /tmp/gen.jpg     # 探照灯
```

方式 B — **message 工具（不稳定，不推荐）：**
```javascript
message({ action: "send", channel: "feishu", target: "user:ou_xxx", media: "/tmp/gen.jpg" })
```
❌ 问题：对 UUID 文件名（无扩展名）的图片可能只显示文件附件，不显示图片

**示例完整流程：**
```bash
# 1. 生图
opencli doubao ask "画一只复古蒸汽火车"

# 2. 下载（复制返回的 URL）
curl -sL -o /tmp/train.jpg "URL" --max-time 30

# 3. 发送（Python 脚本）
python3 ~/.openclaw/scripts/send_image_as_zuoba.py /tmp/train.jpg
```

---

## 生图方式二（备选）：opencli operate Chrome 自动化

**当方式一失败时使用。需要新开 Chrome 窗口，不影响 L 的浏览器。**

### 前提条件
- Chrome 已安装 OpenCLI Browser Bridge 扩展（`opencli operate state` 显示 interactive > 0）
- 扩展需独立 Chrome 实例（不能和 L 的浏览器共用）

### 操作步骤

```bash
# 1. 新开 Chrome 窗口打开豆包（不影响 L 的浏览器）
open -a "Google Chrome" --new-window "https://www.doubao.com/chat/create-image"
sleep 5

# 2. 输入 prompt（元素编号以实际快照为准）
opencli operate type 2 "复古蒸汽火车"
opencli operate click 53   # 点击"图像生成"按钮

# 3. 等待生成
sleep 25

# 4. 提取图片 URL（以实际快照为准）
opencli operate eval "document.querySelectorAll('img[src*=rc_gen_image]')[0].src"

# 5. 下载
curl -sL -o /tmp/gen.jpg "URL" --max-time 30

# 6. 发送（Python 脚本）
python3 ~/.openclaw/scripts/send_image_as_zuoba.py /tmp/gen.jpg
```

### 常见问题
- `opencli operate state` 显示 interactive = 0：扩展断开，重新连接
- 元素编号变化：每次操作前先 `opencli operate snapshot` 确认
- 豆包登录失效：方式一会自动检测，方式二需手动重新登录

---

## 能力清单

| 工具 | 能力 | 状态 | 备注 |
|------|------|------|------|
| 豆包（即梦） | 文生图 | ✅ 推荐 | 方式一/二均可 |
| 即梦网页 | 文生图+视频 | 🔲 待测 | 更高质量 |
| 通义千问 | 文生图 | 🔲 待测 | 待验证 |

---

## ⚠️ 重要规则

**关于发送图片：**
- ❌ 绝对不能直接在消息里粘贴文件路径（如 `/tmp/xxx.jpg`），L 看不到
- ❌ 不要用 `message(media=...)` 发图片（不稳定）
- ✅ 统一用 Python 脚本发送：`send_image_as_*.py`

**关于 Chrome：**
- 方式二需要 Chrome 时，**必须**用 `--new-window` 新开窗口，不影响 L 的浏览器
- 不要用 `open -a "Google Chrome"` 激活 L 已有的 Chrome 实例

---

## 触发词

- "画一只"、"帮我画"
- "生成图片"、"生张图"
- "AI 画"
- "文章配图"、"封面图"
- "发一张图片"
