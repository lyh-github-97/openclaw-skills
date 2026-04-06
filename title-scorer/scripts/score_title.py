#!/usr/bin/env python3
"""
微信公众号标题评分器
分析标题的：搜索指数、点击欲、系列感、去AI味、价值感

Usage:
    python3 score_title.py "你的标题"
"""

import sys
import json
import re

# ============================================================
# 关键词库：影响搜索指数得分 (0-25分)
# ============================================================
HIGH_SEARCH_KEYWORDS = {
    # 人物类（搜索量极高）
    "马斯克": 5, "埃隆": 3, "马斯克新书": 5,
    "特斯拉": 4, "SpaceX": 4, "Twitter": 3, "X推特": 2,
    "马云": 4, "马云最新": 3,
    "雷军": 4, "小米": 3,
    "张一鸣": 3, "字节跳动": 3, "TikTok": 3,
    "王兴": 3, "美团": 3,
    "马化腾": 3, "腾讯": 3,
    "刘强东": 3, "京东": 3,
    "周鸿祎": 2, "360": 2,
    "董明珠": 3, "格力": 3,
    "许家印": 3, "恒大": 3,
    "王健林": 3, "万达": 3,
    "孙正义": 3, "软银": 2,
    "贝索斯": 3, "亚马逊": 3,
    "库克": 3, "苹果": 3,
    "扎克伯格": 3, "Meta": 3, "Facebook": 3,
    "比尔盖茨": 4, "微软": 3,
    "奥尔特曼": 3, "OpenAI": 4, "ChatGPT": 4, "GPT": 3,
    "奥特曼": 2,  # OpenAI CEO，别名
    "黄仁勋": 4, "英伟达": 4, "NVIDIA": 3, "GPU": 2,
    "苏姿丰": 3, "AMD": 3,
    "皮查伊": 2, "Google": 3, "谷歌": 3,
    "李彦宏": 3, "百度": 3,
    "李开复": 2, "创新工场": 2,
    "王慧文": 2, "美团联合创始人": 2,
    # 概念类（搜索量高）
    "第一性原理": 4, "思维模型": 3, "认知升级": 3,
    "创业": 4, "副业": 3, "赚钱": 3, "风口": 3,
    "AI": 4, "人工智能": 4, "大模型": 4, "LLM": 3,
    "自动驾驶": 3, "新能源": 3, "电动车": 3,
    "火星": 3, "太空": 3, "火箭": 3,
    "投资": 3, "理财": 3, "基金": 2, "股票": 3,
    "职场": 3, "晋升": 2, "加薪": 2, "裁员": 3,
    "管理": 3, "领导力": 3, "团队": 2,
    "产品": 3, "运营": 2, "增长": 3,
    "流量": 3, "私域": 3, "变现": 3,
    "短视频": 3, "直播": 3, "抖音": 3, "小红书": 3,
    "出海": 3, "跨境": 3, "全球化": 2,
    "芯片": 4, "半导体": 4, "制裁": 3,
    "经济": 3, "通胀": 3, "衰退": 3, "牛市": 3,
    "房地产": 3, "房价": 3,
    # 情绪类（高传播）
    "崩溃": 2, "暴雷": 3, "倒闭": 3, "裁员": 3,
    "翻身": 2, "逆袭": 2, "暴富": 2, "财务自由": 3,
    "干货": 3, "必看": 2, "收藏": 2,
}

MEDIUM_SEARCH_KEYWORDS = {
    "新书": 2, "新书解读": 3, "新书推荐": 2,
    "读书": 2, "好书": 2, "书单": 2,
    "拆解": 2, "解读": 1, "分析": 1, "干货": 2,
    "深度": 1, "深度好文": 1, "深度分析": 1,
    "复盘": 2, "总结": 1, "年度": 1,
    "方法论": 2, "公式": 2, "法则": 2,
    "秘密": 2, "真相": 2, "内幕": 2, "曝光": 2,
    "秘诀": 2, "诀窍": 1, "技巧": 1,
    "注意": 1, "警告": 2, "提醒": 1,
    "最新": 1, "刚刚": 1, "突发": 2, "重磅": 2,
}

# ============================================================
# 点击欲触发词 (0-25分)
# ============================================================
CLICK_TRIGGERS = {
    # 数字类（数字在标题中有强注意力捕获效果）
    "⑩": 4, "⑪": 4, "⑫": 4, "⑬": 4, "⑭": 4,
    "⑨": 3, "⑧": 3, "⑦": 3, "⑩": 4,
    "①": 2, "②": 2, "③": 2, "④": 3, "⑤": 3, "⑥": 3,
    "10个": 3, "20个": 3, "100个": 3,
    "3个": 2, "5个": 2, "7个": 2,
    "第1次": 3, "第1章": 2,
    # 标点符号（制造悬念）
    "？": 3, "？": 3, "……": 2, "…": 1,
    "！": 1, "：": 1,
    # 好奇驱动
    "为什么": 3, "怎么": 2, "如何": 2,
    "原来": 2, "其实": 1,
    "真相是": 3, "你不知道": 3, "不为人知": 3,
    "这才": 2, "终于": 2, "第一次": 2,
    "和想象中": 2, "以为": 1,
    "值得深思": 2, "睡不着": 3,
    "崩溃": 2, "无语": 2, "扎心": 2,
    "被骂": 2, "翻车": 3, "翻车了": 3,
    "硬核": 3, "炸裂": 2, "逆天": 2,
    "千万别": 2, "不要": 1, "禁止": 2,
    "差距": 2, "碾压": 2, "吊打": 2,
    "太牛了": 2, "太强了": 2, "太绝了": 2,
    # 价值暗示
    "文末领": 3, "免费领": 2, "限时": 2, "仅此一天": 2,
    "内部": 2, "独家": 2, "首次": 2,
}

# ============================================================
# AI味模式（扣分项，0-15分）
# ============================================================
AI_PATTERNS = {
    # 模板套路
    "一文读懂": -4, "一文看懂": -4, "一篇搞懂": -4,
    "关于.*的思考": -3, "对.*的思考": -3,
    "深度好文": -3, "深度解读": -3, "深度分析": -3,
    "干货满满": -3, "全是干货": -3,
    "建议收藏": -3, "建议转发": -3,
    "不容错过": -3, "不可错过": -3,
    "强烈推荐": -3, "推荐指数": -3,
    "内含.*福利": -2, "内含福利": -2,
    # 过度用词
    "字少事大": -4, "话不多说": -3, "直接上": -3,
    "太牛了": -2, "太厉害了": -2, "太绝了": -2,
    "YYDS": -3, "绝了绝了": -2,
    "太香了": -2, "真香": -2,
    "炸裂": -2, "逆天": -2,
    "大佬": -2, "大神": -2, "巨佬": -2,
    "我发现了": -2, "被我找到了": -2,
    # 废话开头
    "大家好": -2, "今天来": -2, "今天给": -2,
    "那么": -1, "所以说": -1, "那么就": -1,
    # 过度衔接
    "接下来": -1, "然后": -1, "接着": -1,
    "综上所述": -3, "总而言之": -3,
    "值得注意的是": -3, "需要注意的是": -3,
    # 空洞承诺
    "具有深远意义": -3, "影响深远": -3,
    "值得高度重视": -3, "必须重视": -3,
}

# ============================================================
# 系列感标记
# ============================================================
SERIES_PATTERNS = [
    r"马斯克新书[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭]",  # 马斯克新书①
    r"马斯克新书\d+",   # 马斯克新书1
    r"埃隆新书[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭]",
    r"埃隆之书[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭]",
    r"《.*》[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭]",  # 《书名》①
    r"第[一二三四五六七八九十]+章",  # 第一章
    r"Chapter\s*\d+",  # Chapter 1
    r"ch_\d+",  # ch_01
]

# ============================================================
# 模糊词（价值感不足，扣分）
# ============================================================
VAGUE_PATTERNS = [
    (r"^.*思考$", -2), ("深度", -1), ("洞察", -1),
    ("感悟", -1), ("体会", -1), ("收获", -1),
    ("分享", -1), ("复盘", -1), ("总结", -1),
    ("漫谈", -2), ("杂谈", -2), ("闲聊", -2),
]

# ============================================================
# 长度限制
# ============================================================
MAX_LENGTH = 64


def score_title(title: str) -> dict:
    """对标题进行多维度评分"""

    score_search = 0       # 搜索指数 (0-25)
    score_click = 0        # 点击欲 (0-25)
    score_series = 0       # 系列感 (0-20)
    score_ai = 0           # 去AI味 (0-15, 满分)
    score_value = 0        # 价值感 (0-15)
    score_length = 0       # 长度合规 (0-5)

    issues = []     # 发现的问题
    suggestions = []  # 优化建议
    positives = []  # 做得好的地方

    # ---------- 1. 搜索指数 ----------
    found_high = []
    for kw, pts in HIGH_SEARCH_KEYWORDS.items():
        if kw in title:
            score_search += pts
            found_high.append(kw)
    for kw, pts in MEDIUM_SEARCH_KEYWORDS.items():
        if kw in title:
            score_search += pts
            found_high.append(kw)

    if found_high:
        positives.append(f"✅ 高搜索词: {', '.join(found_high)}")
    if score_search >= 15:
        score_search = min(score_search, 25)

    # ---------- 2. 点击欲 ----------
    for trigger, pts in CLICK_TRIGGERS.items():
        if trigger in title:
            score_click += pts
    # 数字类额外加成（阿拉伯数字也计算）
    arabic_nums = re.findall(r'\d+[个件次]', title)
    if arabic_nums:
        score_click += len(arabic_nums) * 1
    # 问号检测
    if '？' in title or '?' in title:
        score_click += 3

    if score_click >= 15:
        positives.append("✅ 点击触发词充足（数字/悬念/疑问）")
    elif score_click < 5:
        issues.append("⚠️ 点击触发词不足，建议加入数字、疑问或冲突元素")

    # ---------- 3. 系列感 ----------
    for pat in SERIES_PATTERNS:
        if re.search(pat, title):
            score_series = 20
            positives.append("✅ 系列标识清晰（编号/章节）")
            break

    if score_series == 0:
        issues.append("⚠️ 缺少系列标识，建议加入 ① ② ③ 或章节编号")

    # ---------- 4. 去AI味 ----------
    score_ai = 15  # 满分基准
    ai_hits = []
    for pattern, penalty in AI_PATTERNS.items():
        if re.search(pattern, title):
            score_ai += penalty
            ai_hits.append(pattern)
    if ai_hits:
        issues.append(f"🚫 AI味模式: {', '.join(set(ai_hits))}")
        suggestions.append("避免模板套路，用更自然的表达替代")

    # ---------- 5. 价值感 ----------
    score_value = 10  # 基准分
    for pattern, penalty in VAGUE_PATTERNS:
        if re.search(pattern, title):
            score_value += penalty
    if any(kw in title for kw in ["文末领", "免费", "限时", "领取", "下载", "资料"]):
        score_value += 3
        positives.append("✅ 包含行动引导/福利钩子")
    if any(kw in title for kw in ["特斯拉", "SpaceX", "火箭", "电动车", "火星"]):
        score_value += 2

    # ---------- 6. 长度合规 ----------
    title_len = len(title)
    if title_len <= MAX_LENGTH:
        score_length = 5
    elif title_len <= MAX_LENGTH + 10:
        score_length = 3
        issues.append(f"⚠️ 标题偏长({title_len}字)，建议控制在64字以内")
    else:
        issues.append(f"🚫 标题过长({title_len}字)，超过微信限制64字")

    # ---------- 总体 ----------
    total = score_search + score_click + score_series + max(0, score_ai) + max(0, score_value) + score_length

    # 等级
    if total >= 85:
        grade = "A+"
    elif total >= 75:
        grade = "A"
    elif total >= 65:
        grade = "B+"
    elif total >= 55:
        grade = "B"
    elif total >= 45:
        grade = "C"
    else:
        grade = "D"

    return {
        "title": title,
        "total_score": total,
        "grade": grade,
        "dimensions": {
            "搜索指数": {"score": min(score_search, 25), "max": 25},
            "点击欲": {"score": min(score_click, 25), "max": 25},
            "系列感": {"score": score_series, "max": 20},
            "去AI味": {"score": max(0, score_ai), "max": 15},
            "价值感": {"score": max(0, score_value), "max": 15},
            "长度合规": {"score": score_length, "max": 5},
        },
        "positives": positives,
        "issues": issues,
        "suggestions": suggestions,
        "title_length": title_len,
    }


def print_report(result: dict):
    title = result["title"]
    dims = result["dimensions"]

    print()
    print("=" * 60)
    print(f"📝 标题: {title}")
    print(f"📊 总分: {result['total_score']}/100  |  等级: {result['grade']}  |  字数: {result['title_length']}")
    print("-" * 60)

    print("\n📐 维度评分:")
    bar_max = 20
    for dim, data in dims.items():
        score = data["score"]
        maximum = data["max"]
        pct = score / maximum if maximum > 0 else 0
        bar_len = int(pct * bar_max)
        bar = "█" * bar_len + "░" * (bar_max - bar_len)
        print(f"  {dim:<8} {bar} {score}/{maximum}")

    if result["positives"]:
        print("\n✨ 亮点:")
        for p in result["positives"]:
            print(f"  {p}")

    if result["issues"]:
        print("\n⚠️ 问题:")
        for issue in result["issues"]:
            print(f"  {issue}")

    if result["suggestions"]:
        print("\n💡 优化建议:")
        for s in result["suggestions"]:
            print(f"  {s}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 score_title.py \"你的标题\"")
        sys.exit(1)

    title = sys.argv[1]
    result = score_title(title)
    print_report(result)

    # JSON output if requested
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
