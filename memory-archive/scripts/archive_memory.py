#!/usr/bin/env python3
"""
memory_archive.py
将 MEMORY.md 中超过 30 天的条目归档到 monthly archive 文件。
"""
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_FILE = WORKSPACE / "MEMORY.md"
ARCHIVE_DIR = WORKSPACE / "memory" / "archive"
BACKUP_FILE = WORKSPACE / "memory" / "MEMORY.md.bak"
CUTOFF_DAYS = 30

# 固定规则标题关键词（包含这些关键词的 ## 标题不是日期条目）
FIXED_TITLE_KEYWORDS = [
    "重要规则", "执行任务规则", "模型切换时同步记忆", "主动学习原则",
    "记住账号密码", "模型切换", "mimo 模型", "minimax Token", "模型缓存",
    "VPN 重启", "VPN 管理", "渠道记忆共享", "技能管理规则", "Clash 节点",
    "日报格式", "记忆管理原则", "SOUL.md 核心原则", "Python 版 MetaClaw",
    "OpenClaw 生态", "claw123 龙虾导航", "研研 Plan B", "Agent Nickname",
    "技能清单", "Cron 任务失败", "待提交反馈", "QQ 开放平台账号",
    "Context 防溢出", "Gateway 绝对底线", "Gateway 重启", "Gateway 操作规则",
    "说话规则", "关于记忆管理", "关于主动性", "Silent Replies", "Heartbeats",
    "2026-03-25 今天", "2026-03-26", "2026-03-27", "2026-03-28",
]

# 固定顶部标题（精确匹配）
FIXED_TOP_TITLES = {"# 重要规则", "# IDENTITY.md", "# USER.md", "# SOUL.md", "# AGENTS.md"}


def is_fixed_rule_title(title: str) -> bool:
    """判断一个 ## 标题是否是固定规则（不是日期条目）"""
    for kw in FIXED_TITLE_KEYWORDS:
        if kw in title:
            return True
    return False


def extract_date_from_title(title: str):
    """从标题中提取日期字符串（如 '2026-03-29'）"""
    # 匹配各种格式：## 标题(2026-03-29) 或 ## 2026-03-29 标题
    patterns = [
        r'((?:19|20)\d{2}-\d{2}-\d{2})',  # YYYY-MM-DD anywhere
    ]
    for pat in patterns:
        m = re.search(pat, title)
        if m:
            return m.group(1)
    return None


def split_fixed_and_entries(lines: list) -> tuple[list, list]:
    """
    将 MEMORY.md 内容分成[固定规则区]和[日期条目区]。
    固定规则区：开头的非日期条目内容（直到遇到第一个日期条目标题）
    """
    fixed_lines = []
    entry_lines = []
    in_entries = False

    for line in lines:
        stripped = line.strip()
        is_title = stripped.startswith('#')

        if not in_entries and is_title:
            # 检查是否是日期条目标题
            date = extract_date_from_title(stripped)
            if date:
                # 是日期条目，检查是否被固定关键词排除
                if not is_fixed_rule_title(stripped):
                    # 第一个真正的日期条目，开始 entries 区
                    in_entries = True
                    entry_lines.append(line)
                    continue

            # 不是日期条目（或被排除），仍在 fixed 区
            fixed_lines.append(line)
            continue

        entry_lines.append(line)

    return fixed_lines, entry_lines


def parse_entries(entry_lines: list) -> list:
    """从条目行列表中提取各个日期条目"""
    DATE_HDR = re.compile(r'^##?\s+.+?(\d{4}-\d{2}-\d{2}).*$')
    entries = []
    current = None
    current_lines = []

    for line in entry_lines:
        m = DATE_HDR.match(line.strip())
        if m:
            date_str = m.group(1)
            # 验证是有效日期
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except:
                current_lines.append(line)
                continue

            # 检查是否是固定规则（排除）
            if is_fixed_rule_title(line.strip()):
                current_lines.append(line)
                continue

            if current:
                entries.append({'date': current, 'lines': current_lines})
            current = date_str
            current_lines = [line]
        else:
            current_lines.append(line)

    if current:
        entries.append({'date': current, 'lines': current_lines})

    return entries


def main():
    print(f"========== Memory Archive ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ==========")

    if not MEMORY_FILE.exists():
        print("❌ MEMORY.md 不存在")
        return

    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 分离固定区和条目区
    fixed_lines, entry_lines = split_fixed_and_entries(lines)
    print(f"📋 固定内容: {len(fixed_lines)} 行")
    print(f"📝 条目内容: {len(entry_lines)} 行")

    # 解析条目
    entries = parse_entries(entry_lines)
    print(f"📌 共 {len(entries)} 个条目")

    cutoff = datetime.now() - timedelta(days=CUTOFF_DAYS)
    print(f"📅 归档线: {cutoff.strftime('%Y-%m-%d')}（{CUTOFF_DAYS}天前）")

    # 分类
    to_archive = [e for e in entries if datetime.strptime(e['date'], '%Y-%m-%d') < cutoff]
    to_keep = [e for e in entries if datetime.strptime(e['date'], '%Y-%m-%d') >= cutoff]

    print(f"📦 待归档: {len(to_archive)} 条")
    print(f"📌 保留: {len(to_keep)} 条")

    if to_archive:
        for e in to_archive:
            title_line = e['lines'][0].strip() if e['lines'] else '?未知?'
            print(f"   → {e['date']}: {title_line[:60]}")

    # 备份
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(MEMORY_FILE, BACKUP_FILE)
    print(f"\n✅ 备份: {BACKUP_FILE.name}")

    if not to_archive:
        print("✅ 无需归档，完成")
        return

    # 写归档文件（按月）
    archive_by_month = {}
    for e in to_archive:
        month = e['date'][:7]
        if month not in archive_by_month:
            archive_by_month[month] = []
        archive_by_month[month].append(e)

    for month, month_entries in archive_by_month.items():
        archive_file = ARCHIVE_DIR / f"{month}.md"
        if archive_file.exists():
            with open(archive_file, 'r') as f:
                existing = f.read().rstrip()
        else:
            existing = f"# {month} 记忆归档\n\n（由 memory-archive skill 自动生成）\n"

        new_content = existing.rstrip() + '\n\n'
        for e in month_entries:
            new_content += '---\n\n' + '\n'.join(e['lines']).strip() + '\n\n'

        with open(archive_file, 'w') as f:
            f.write(new_content.rstrip() + '\n')
        print(f"  ✅ {month} ({len(month_entries)}条) → {archive_file.name}")

    # 重写 MEMORY.md
    fixed_content = '\n'.join(fixed_lines).rstrip()
    new_parts = [fixed_content] if fixed_content else []
    for e in to_keep:
        new_parts.append('\n'.join(e['lines']).strip())

    new_content = '\n\n'.join(new_parts).rstrip() + '\n'

    with open(MEMORY_FILE, 'w') as f:
        f.write(new_content)

    print(f"\n✅ MEMORY.md 已更新：保留 {len(to_keep)} 条，近期条目")
    print(f"   旧内容备份在: {BACKUP_FILE}")


if __name__ == '__main__':
    main()
