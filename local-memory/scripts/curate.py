#!/usr/bin/env python3
"""
curate.py - 从 memory/ 文件挖掘知识，存入结构化 knowledge_tree.json
用法:
  python3 curate.py              # 从今日 memory 文件挖掘
  python3 curate.py --since 3   # 最近N天的文件
  python3 curate.py --file path  # 指定文件
  python3 curate.py --summary "决策内容" --cat error --tag "gateway"
"""
import json, datetime, argparse, re, sys
from pathlib import Path

TREE_PATH = Path("/Users/liyaohua/.openclaw/skills/local-memory/knowledge/knowledge_tree.json")
MEMORY_DIR = Path("/Users/liyaohua/.openclaw/workspace/memory")

def load_tree():
    with open(TREE_PATH) as f:
        return json.load(f)

def save_tree(tree):
    with open(TREE_PATH, "w") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)

def read_memory_files(since_days=None, specific_file=None):
    if specific_file:
        p = Path(specific_file)
        if p.exists():
            return [(p.name, p.read_text())]
        return []
    files = sorted(MEMORY_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if since_days:
        cutoff = datetime.datetime.now() - datetime.timedelta(days=since_days)
        files = [f for f in files if datetime.datetime.fromtimestamp(f.stat().st_mtime) >= cutoff]
    return [(f.name, f.read_text()) for f in files if f.name != "knowledge_tree.json"]

def add_entry(category, content, tags=None, source_file=None):
    """添加知识条目"""
    tree = load_tree()
    entry = {
        "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        "timestamp": datetime.datetime.now().isoformat(),
        "category": category,
        "content": content.strip(),
        "tags": tags or [],
        "source": source_file,
        "confidence": "high"
    }
    tree["entries"].insert(0, entry)
    tree["_meta"]["total_entries"] = len(tree["entries"])
    tree["_meta"]["last_updated"] = datetime.date.today().isoformat()
    save_tree(tree)
    print(f"✅ 添加 [{category}] {entry['id']}: {content[:60]}...")

def extract_from_text(filename, content):
    """从文本内容中提取知识条目"""
    # 简单规则：识别 ## 或 ### 开头的段落作为知识点
    entries = []
    lines = content.split("\n")
    current = []
    in_entry = False

    for line in lines:
        if line.startswith("## ") and len(line) > 5:
            if current:
                text = "\n".join(current).strip()
                if len(text) > 20:
                    entries.append(text)
            current = [line]
            in_entry = True
        elif in_entry:
            current.append(line)

    if current:
        text = "\n".join(current).strip()
        if len(text) > 20:
            entries.append(text)

    return entries

def daily_mine(since_days=1):
    """每日挖掘：读最近 memory 文件，提炼知识"""
    files = read_memory_files(since_days=since_days)
    print(f"📖 读取 {len(files)} 个 memory 文件...")

    new_count = 0
    for fname, content in files:
        entries = extract_from_text(fname, content)
        for entry in entries:
            # 跳过太短或重复检测
            if len(entry) < 50:
                continue
            # 简单去重
            tree = load_tree()
            if any(e["content"][:80] == entry[:80] for e in tree["entries"][:20]):
                continue
            # 分类推断（关键词匹配）
            cat = infer_category(entry)
            add_entry(cat, entry, source_file=fname)
            new_count += 1

    print(f"\n🎉 挖掘完成: 新增 {new_count} 条知识")

def infer_category(text):
    """根据内容推断分类"""
    text_lower = text.lower()
    if any(w in text_lower for w in ["错误", "error", "失败", "bug", "教训", "问题"]):
        return "error"
    if any(w in text_lower for w in ["配置", "config", "设置", "安装", "方案"]):
        return "config"
    if any(w in text_lower for w in ["决策", "决定", "选择", "判断"]):
        return "decision"
    if any(w in text_lower for w in ["学到", "知识", "认知", "规律"]):
        return "knowledge"
    if any(w in text_lower for w in ["任务", "流程", "完成了"]):
        return "task"
    if any(w in text_lower for w in ["偏好", "习惯", "L说", "L的"]):
        return "pattern"
    return "knowledge"

def main():
    parser = argparse.ArgumentParser(description="本地记忆知识挖掘工具")
    parser.add_argument("--since", type=int, help="挖掘最近N天")
    parser.add_argument("--file", type=str, help="指定文件路径")
    parser.add_argument("--summary", type=str, help="直接添加知识条目内容")
    parser.add_argument("--cat", type=str, default="knowledge", help="分类")
    parser.add_argument("--tag", nargs="*", help="标签")
    args = parser.parse_args()

    if args.summary:
        add_entry(args.cat, args.summary, args.tag)
    elif args.file:
        p = Path(args.file)
        if p.exists():
            content = p.read_text()
            for entry in extract_from_text(p.name, content):
                if len(entry) > 30:
                    cat = infer_category(entry)
                    add_entry(cat, entry, source_file=p.name)
        else:
            print(f"文件不存在: {args.file}")
    else:
        daily_mine(since_days=args.since or 1)

if __name__ == "__main__":
    main()
