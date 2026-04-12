#!/usr/bin/env python3
"""
batch_analyze.py — 每日反思缓冲区批量分析
读取 reflect-buffer.md，找出模式，生成改进建议
"""
import re
import sys
from pathlib import Path
from datetime import datetime

BUFFER = Path.home() / ".openclaw/workspace/memory/reflect-buffer.md"
SUGGESTIONS = Path.home() / ".openclaw/workspace/memory/reflect-suggestions.md"
SOUL = Path.home() / ".openclaw/workspace/SOUL.md"

def read_buffer():
    if not BUFFER.exists():
        return []
    content = BUFFER.read_text()
    # Split by ## [反思] headers
    entries = re.split(r"(?=## \[反思\])", content)
    return [e.strip() for e in entries if e.strip()]

def extract_problems(entries):
    """找出重复出现的问题模式"""
    problems = []
    for e in entries:
        if "问题" in e or "根因" in e or "失败" in e:
            problems.append(e)
    return problems

def generate_suggestions(entries):
    """生成改进建议"""
    suggestions = []
    
    # 提取所有改进建议
   改进_lines = []
    for e in entries:
        if "改进" in e or "建议" in e:
            lines = [l.strip() for l in e.split("\n") if l.strip()]
            for l in lines:
                if "**改进**" in l or "**建议**" in l:
                    改进_lines.append(l)
    
    # 去重
    seen = set()
    unique = []
    for l in 改进_lines:
        key = re.sub(r"\*\*|改进：|建议：", "", l).strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(l)
    
    return unique

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 反思缓冲区分析开始...")
    
    entries = read_buffer()
    if not entries:
        print("缓冲区为空，无需分析")
        return
    
    print(f"共 {len(entries)} 条反思记录")
    
    problems = extract_problems(entries)
    suggestions = generate_suggestions(entries)
    
    # 生成报告
    report = f"""# 反思改进建议 — {datetime.now().strftime('%Y-%m-%d')}

## 概览

- 反思总数：{len(entries)}
- 问题记录：{len(problems)}
- 有效建议：{len(suggestions)}

---

## 改进建议（请确认后执行）

"""
    for i, s in enumerate(suggestions, 1):
        report += f"{i}. {s}\n"
    
    report += """
---

## 操作

- 确认后运行：`python3 ~/.openclaw/skills/self-reflect/scripts/apply_suggestions.py`
- 或直接修改对应文件

*由 self-reflect skill 自动生成*
"""
    
    SUGGESTIONS.write_text(report)
    print(f"建议已写入：{SUGGESTIONS}")
    print(f"共 {len(suggestions)} 条建议")

if __name__ == "__main__":
    main()
