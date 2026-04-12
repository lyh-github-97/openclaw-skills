#!/usr/bin/env python3
"""
apply_suggestions.py — 将确认的改进建议写入 SOUL.md
执行前需要人类逐条确认
"""
import sys
from pathlib import Path
from datetime import datetime

SUGGESTIONS = Path.home() / ".openclaw/workspace/memory/reflect-suggestions.md"
SOUL = Path.home() / ".openclaw/workspace/SOUL.md"
BUFFER = Path.home() / ".openclaw/workspace/memory/reflect-buffer.md"

def main():
    if not SUGGESTIONS.exists():
        print("没有找到建议文件，请先运行 batch_analyze.py")
        return
    
    content = SUGGESTIONS.read_text()
    print("=== 待写入建议 ===")
    print(content[:2000])
    
    # 从建议文件提取具体改进内容
    lines = content.split("\n")
    improvements = []
    for l in lines:
        if "**改进**" in l or "**建议**" in l:
            text = re.sub(r"\*\*|改进：|建议：", "", l).strip()
            if text:
                improvements.append(text)
    
    if not improvements:
        print("没有可写入的改进内容")
        return
    
    print(f"\n将写入 {len(improvements)} 条改进到 SOUL.md")
    print("\n具体内容：")
    for i, imp in enumerate(improvements, 1):
        print(f"  {i}. {imp}")
    
    print("\n此操作不可逆，建议先备份 SOUL.md")
    print("继续请输入 'yes'：", end=" ")
    
    # 非交互模式：直接执行（人类已确认）
    if len(sys.argv) > 1 and sys.argv[1] == "--confirm":
        confirmed = "yes"
    else:
        confirmed = input().strip()
    
    if confirmed.lower() != "yes":
        print("已取消")
        return
    
    # 追加到 SOUL.md
    timestamp = datetime.now().strftime("%Y-%m-%d")
    section = f"""

---

## 改进记录（{timestamp}）

"""
    for imp in improvements:
        section += f"- {imp}\n"
    
    with open(SOUL, "a") as f:
        f.write(section)
    
    print(f"已写入 SOUL.md（{len(improvements)} 条）")
    
    # 清空缓冲区（已完成闭环）
    if BUFFER.exists():
        BUFFER.write_text("")
        print("缓冲区已清空")

if __name__ == "__main__":
    import re
    main()
