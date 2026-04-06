#!/usr/bin/env python3
"""
retrieve.py - 根据当前对话/问题检索相关记忆
用法:
  python3 retrieve.py "今天我们讨论了什么"
  python3 retrieve.py --query "L的配置偏好" --limit 5
"""
import json, sys, argparse
from pathlib import Path

TREE_PATH = Path("/Users/liyaohua/.openclaw/skills/local-memory/knowledge/knowledge_tree.json")

def load_tree():
    with open(TREE_PATH) as f:
        return json.load(f)

def score_entry(entry, query):
    """简单关键词匹配打分"""
    text = entry["content"].lower()
    query_lower = query.lower()
    score = 0
    for word in query_lower.split():
        word = word.strip()
        if len(word) < 2:
            continue
        score += text.count(word) * 2
        if word in entry.get("tags", []):
            score += 5
        if word in entry.get("category", ""):
            score += 3
    return score

def retrieve(query, limit=5, category=None):
    tree = load_tree()
    entries = tree["entries"]
    if category:
        entries = [e for e in entries if e.get("category") == category]

    scored = [(score_entry(e, query), e) for e in entries]
    scored.sort(key=lambda x: -x[0])
    return scored[:limit]

def format_entry(entry, score=None):
    cat_emoji = {
        "error": "🔴",
        "config": "⚙️",
        "decision": "📌",
        "knowledge": "💡",
        "task": "✅",
        "pattern": "👤",
    }
    emoji = cat_emoji.get(entry.get("category"), "📝")
    ts = entry.get("timestamp", "")[:10]
    source = f"[{entry.get('source', '')}]" if entry.get("source") else ""
    header = f"{emoji} [{entry.get('category')}] {ts} {source}"
    content = entry["content"][:200] + ("..." if len(entry["content"]) > 200 else "")
    if score is not None and score > 0:
        return f"{header}\n  得分:{score} | {content}\n"
    return f"{header}\n  {content}\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", default="", help="查询内容")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--cat", default=None, help="只查某分类")
    parser.add_argument("--all", action="store_true", help="列出全部")
    args = parser.parse_args()

    tree = load_tree()

    if args.all:
        print(f"📚 知识树共 {tree['_meta']['total_entries']} 条\n")
        for entry in tree["entries"][:20]:
            print(format_entry(entry))
        return

    if not args.query:
        print("用法: retrieve.py <查询内容> 或 --all")
        return

    results = retrieve(args.query, limit=args.limit, category=args.cat)
    print(f"🔍 查询: {args.query}\n")
    if not results:
        print("未找到相关记忆")
        return
    print(f"找到 {len(results)} 条相关记忆:\n")
    for score, entry in results:
        print(format_entry(entry, score))

if __name__ == "__main__":
    main()
