#!/usr/bin/env python3
"""
将日记文本转换为精美的图片。
使用 Playwright 渲染 HTML 并截图。
"""
import sys
import os
import re
import json
import time
import subprocess
import tempfile
import shutil

DIARY_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500&display=swap');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  width: 1200px;
  min-height: 1600px;
  background: #FFF8F0;
  font-family: 'Noto Serif SC', 'STSong', 'SimSun', serif;
  color: #2C1810;
  padding: 72px 80px 80px 80px;
  position: relative;
}}
body::before, body::after {{
  content: '';
  position: fixed;
  width: 80px;
  height: 80px;
  border-color: #C9A96E;
  border-style: solid;
  opacity: 0.5;
}}
body::before {{ top: 30px; left: 30px; border-width: 3px 0 0 3px; }}
body::after {{ bottom: 30px; right: 30px; border-width: 0 3px 3px 0; }}
.header {{ text-align: center; margin-bottom: 8px; }}
.header-rule {{ width: 120px; height: 2px; background: linear-gradient(90deg, transparent, #C9A96E, transparent); margin: 0 auto 24px auto; }}
.date-title {{ font-family: 'Noto Serif SC', serif; font-size: 52px; font-weight: 700; color: #2C1810; letter-spacing: 4px; margin-bottom: 8px; }}
.subtitle {{ font-family: 'Noto Sans SC', sans-serif; font-size: 14px; font-weight: 300; color: #9A8A7A; letter-spacing: 8px; text-transform: uppercase; }}
.section {{ margin-top: 40px; }}
.section-title {{ display: flex; align-items: center; gap: 12px; font-size: 22px; font-weight: 600; color: #2C1810; margin-bottom: 18px; padding-bottom: 10px; border-bottom: 1px solid #E8DCC8; }}
.section-title .emoji {{ font-size: 24px; }}
.section-title .text {{ flex: 1; }}
.section-title::after {{ content: ''; flex: 1; height: 1px; background: #E8DCC8; }}
.body-text {{ font-size: 17px; line-height: 2; color: #3D2B1F; text-align: justify; padding-left: 4px; }}
.bullet-list {{ list-style: none; padding: 0; }}
.bullet-item {{ display: flex; gap: 16px; font-size: 17px; line-height: 2; color: #3D2B1F; padding: 8px 0 8px 4px; border-bottom: 1px dashed #EDE4D6; }}
.bullet-item:last-child {{ border-bottom: none; }}
.bullet-marker {{ color: #C9A96E; font-size: 18px; flex-shrink: 0; padding-top: 2px; }}
.bullet-text {{ flex: 1; }}
.bullet-text strong {{ color: #2C1810; font-weight: 600; }}
.mid-rule {{ width: 60px; height: 1px; background: #C9A96E; margin: 44px auto; opacity: 0.6; }}
.check-item {{ display: flex; gap: 12px; font-size: 17px; line-height: 2; color: #3D2B1F; padding: 6px 0 6px 4px; }}
.check-marker {{ color: #6B8E5A; font-size: 16px; flex-shrink: 0; padding-top: 2px; }}
.footer {{ position: fixed; bottom: 40px; left: 80px; right: 80px; display: flex; justify-content: space-between; align-items: center; font-family: 'Noto Sans SC', sans-serif; font-size: 12px; color: #BBA88A; letter-spacing: 2px; }}
.footer .author {{ color: #9A8A7A; font-weight: 500; }}
</style>
</head>
<body>

<div class="header">
  <div class="header-rule"></div>
  <div class="date-title">{date_emoji} 日记 · {date}</div>
  <div class="subtitle">爪巴 · AI 助手</div>
</div>

{content}

<div class="footer">
  <span class="author">爪巴</span>
  <span>{date}</span>
</div>

</body>
</html>"""

SECTION_HTML = """
<div class="section">
  <div class="section-title">
    <span class="emoji">{emoji}</span>
    <span class="text">{title}</span>
  </div>
  {body}
</div>
"""

SECTION_KEYWORDS = sorted([
    # 标准板块（固定格式）
    '今日最值得记住的一件事',
    '重要决策和改动',
    '新的学习和认知',
    '做得不够好的地方',
    '明天要做的事',
    '不够好的地方',
    '学习和认知',
    '自我反省',
    '自我反思',
    '做得不够好',
    '重要决策',
    '最值得记住',
    '明天要',
], key=len, reverse=True)


def get_section_emoji(title):
    """根据标题关键词匹配 emoji，优先精确匹配。"""
    # 精确词匹配
    precise = {
        '最值得记住': '🌟',
        '重要决策': '📌',
        '决策和改动': '📌',
        '学习和认知': '💡',
        '自主学习': '💡',
        '新发现': '💡',
        '不够好': '⚠️',
        '自我反省': '⚠️',
        '自我反思': '⚠️',
        '错误': '⚠️',
        '不足': '⚠️',
        '明天': '✅',
    }
    for k, v in precise.items():
        if k in title:
            return v
    # 语义兜底
    if any(k in title for k in ['启示', '洞察', '领悟']):
        return '🌟'
    if any(k in title for k in ['关系', '信任', '伙伴']):
        return '🌟'
    return '📝'


def parse_diary(text, date):
    """解析日记文本，生成 HTML。优先标准 **标题** 格式，兜底嵌入式格式。"""
    lines = text.strip().split('\n')

    # 检测是否有 **标题** 格式
    has_markdown = any(
        (l.strip().startswith('**') and l.strip().endswith('**')) or l.strip().startswith('## ')
        for l in lines if l.strip()
    )

    if has_markdown:
        return parse_diary_markdown(text)
    return parse_diary_embedded(text)


def parse_diary_markdown(text):
    """标准 **标题** 格式（逐行遍历）。"""
    lines = text.strip().split('\n')
    sections = []
    current_section = None
    current_items = []
    current_body = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        is_md = (line.startswith('**') and line.endswith('**')) or line.startswith('## ')
        if is_md:
            if current_section:
                sections.append(finish_section(current_section, current_items, current_body))
            title = line[3:].strip() if line.startswith('## ') else line.strip('* ')
            current_section = {'title': title, 'emoji': get_section_emoji(title)}
            current_items = []
            current_body = []
        elif current_section:
            if line.startswith('- **') or line.startswith('• **') or (line.startswith('**') and '**' in line[2:]):
                current_items.append(line.lstrip('-• '))
            else:
                current_body.append(line)

    if current_section:
        sections.append(finish_section(current_section, current_items, current_body))

    return build_sections_html(sections)


def parse_diary_embedded(text):
    """嵌入式格式：按关键词在文本中的位置切分 body。"""
    all_matches = []
    for kw in SECTION_KEYWORDS:
        for m in re.finditer(re.escape(kw), text):
            all_matches.append((m.start(), kw))
    all_matches.sort(key=lambda x: x[0])

    if not all_matches:
        return ''

    sections = []
    prev_end = 0
    for idx, (pos, kw) in enumerate(all_matches):
        body_chunk = text[prev_end:pos].strip()
        # 去掉日记标题行等 preamble
        body_lines = [l for l in body_chunk.split('\n')
                      if l.strip() and '日记' not in l
                      and l.strip() not in ['📅', '🌟', '📌', '💡', '⚠️', '✅']]
        body = ' '.join(body_lines)
        # 如果 body 为空（第一个 section 的 preamble 过滤完了），说明内容在下一个 chunk
        # 这种情况下：跳过添加，等下一个 keyword 来认领
        if body:
            sections.append({'title': kw, 'emoji': get_section_emoji(kw),
                               'body_text': body, 'items': []})
        prev_end = pos + len(kw)

    # 最后一块：归属已有 sections 的最后一个（合并）
    tail = text[prev_end:].strip()
    tail_lines = [l for l in tail.split('\n') if l.strip() and '日记' not in l]
    if tail_lines:
        combined_tail = ' '.join(tail_lines)
        if sections:
            sections[-1]['body_text'] += ' ' + combined_tail
        else:
            sections.append({'title': '其他', 'emoji': '📝',
                               'body_text': combined_tail, 'items': []})

    return build_sections_html(sections)


def finish_section(sec, items, body_lines):
    return {
        'title': sec['title'],
        'emoji': sec['emoji'],
        'body_text': ' '.join(body_lines) if body_lines else '',
        'items': items
    }


def build_body(body_text, items):
    parts = []
    if body_text:
        parts.append(f'<p class="body-text">{body_text}</p>')
    if items:
        list_items = []
        for item in items:
            if '**' in item:
                def repl(m):
                    return f'<strong>{m.group(1)}</strong>'
                item = re.sub(r'\*\*(.+?)\*\*', repl, item)
            list_items.append(
                f'<li class="bullet-item"><span class="bullet-marker">◆</span>'
                f'<span class="bullet-text">{item}</span></li>'
            )
        parts.append(f'<ul class="bullet-list">{"".join(list_items)}</ul>')
    return '\n'.join(parts)


def build_sections_html(sections):
    html_parts = []
    for idx, sec in enumerate(sections):
        if sec.get('body_text') or sec.get('items'):
            html_parts.append(SECTION_HTML.format(
                emoji=sec['emoji'],
                title=sec['title'],
                body=build_body(sec.get('body_text', ''), sec.get('items', []))
            ))
            if idx < len(sections) - 1:
                html_parts.append('<div class="mid-rule"></div>')
    return '\n'.join(html_parts)


def render_screenshot(html_path, output_path):
    """使用 Playwright 截图。"""
    # 直接硬编码路径，避免 LaunchAgent 环境下找不到 npm
    npm_global = '/Users/liyaohua/.npm-global/lib/node_modules'
    playwright_path = os.path.join(npm_global, 'playwright')

    script = f"""
const {{ chromium }} = require('{playwright_path}');
const path = require('path');
(async () => {{
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const fileUrl = 'file://' + path.resolve('{html_path}');
  await page.goto(fileUrl, {{ waitUntil: 'networkidle', timeout: 15000 }});
  const height = await page.evaluate(() => document.body.scrollHeight);
  await page.setViewportSize({{ width: 1280, height: Math.max(height, 900) }});
  await page.screenshot({{
    path: '{output_path}',
    fullPage: true,
    type: 'png'
  }});
  await browser.close();
  console.log('OK:' + '{output_path}');
}})().catch(e => {{ console.error('ERROR:' + e.message); process.exit(1); }});
"""
    result = subprocess.run(
        ['/usr/local/bin/node', '-e', script],
        capture_output=True, text=True, timeout=30,
        env={**os.environ, 'NODE_PATH': npm_global}
    )
    if result.returncode != 0 or not result.stdout.strip().startswith('OK'):
        raise RuntimeError(f"Playwright failed: {result.stderr}\n{result.stdout}")
    print(result.stdout.strip())


def diary_to_image(diary_text, date, output_path):
    """主函数：将日记文本转为图片。"""
    content_html = parse_diary(diary_text, date)

    html = DIARY_HTML_TEMPLATE.format(
        date_emoji='📅',
        date=date,
        content=content_html
    )

    tmp_dir = tempfile.mkdtemp(prefix='diary_')
    html_path = os.path.join(tmp_dir, 'diary.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    try:
        render_screenshot(html_path, output_path)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return output_path


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: diary_image.py <diary_text_file> <output_png> [date]")
        sys.exit(1)

    diary_file = sys.argv[1]
    output_path = os.path.abspath(sys.argv[2])
    date = sys.argv[3] if len(sys.argv) > 3 else time.strftime('%Y-%m-%d')

    with open(diary_file, 'r', encoding='utf-8') as f:
        diary_text = f.read()

    diary_to_image(diary_text, date, output_path)
    print(f"Image saved: {output_path}")
