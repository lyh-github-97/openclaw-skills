#!/usr/bin/env python3
"""
sync.py - 同步 skills 目录到 Skills 管理仪表盘（Bitable）
使用 lark-cli 读写 Bitable
"""
import os, json, subprocess

SKILLS_DIRS = [
    "/Users/liyaohua/.openclaw/skills",
    "/Users/liyaohua/.openclaw/workspace/skills",
]
BITABLE_APP = "Z5NZbFLxHamyHJsA9DwcZJ3Vnfe"
BITABLE_TABLE = "tblaHFB38BKBAHWv"

def get_skill_meta(skill_path):
    desc = trigger = version = ""
    md_path = os.path.join(skill_path, "SKILL.md")
    if os.path.exists(md_path):
        with open(md_path) as f:
            content = f.read()
        for line in content.split("\n"):
            if line.startswith("description:"):
                desc = line.split(":", 1)[1].strip().rstrip(".")
            if "触发词" in line:
                parts = line.split("触发词", 1)
                if len(parts) > 1:
                    trigger = parts[1].strip().lstrip(":：").strip()
    return desc, trigger

def infer_agent(skill_path):
    if "/workspace/skills/" in skill_path:
        return "爪巴(主)"
    if "/agents/" in skill_path:
        agent_map = {"finance": "财财", "research": "研研", "spotlight": "探照灯", "learner": "学习搭子"}
        parts = skill_path.split("/agents/")[1].split("/")
        return agent_map.get(parts[0], parts[0])
    return "爪巴(主)"

def infer_type(name):
    n = name.lower()
    if any(x in n for x in ["cron", "daily", "diary"]): return "cron"
    if any(x in n for x in ["research", "report", "study", "learn"]): return "研究"
    if any(x in n for x in ["system", "backup", "archive", "health"]): return "系统"
    return "工具"

def scan_skills():
    skills = {}
    for base_dir in SKILLS_DIRS:
        if not os.path.exists(base_dir): continue
        for name in os.listdir(base_dir):
            path = os.path.join(base_dir, name)
            if os.path.isdir(path) and not name.startswith("."):
                desc, trigger = get_skill_meta(path)
                agent = infer_agent(path)
                skill_type = infer_type(name)
                skills[name] = {
                    "功能描述": desc,
                    "关联Agent": agent,
                    "类型": skill_type,
                    "安装状态": "已安装",
                    "用途/触发词": trigger,
                }
    return skills

def lark_cli(args):
    cmd = ["lark-cli"] + args
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except:
        return {}

def main():
    skills = scan_skills()
    print(f"扫描到 {len(skills)} 个 skills")

    # 读取仪表盘现有记录
    data = lark_cli(["api", "GET",
        f"/open-apis/bitable/v1/apps/{BITABLE_APP}/tables/{BITABLE_TABLE}/records",
        "--as", "user", "--page-all", "--page-size", "500"])

    existing = {}
    if data.get("ok"):
        for item in data["data"]["items"]:
            fname = item["fields"].get("技能名称", "")
            if fname:
                existing[fname] = item["record_id"]

    # 对比：新增
    to_add = set(skills.keys()) - set(existing.keys())
    # 对比：多余（目录没有但仪表盘有）
    to_remove = set(existing.keys()) - set(skills.keys())

    print(f"新增: {len(to_add)}  {to_add}")
    print(f"多余: {len(to_remove)}  {to_remove}")

    # 目前只打印，不自动写（需要完整 bitable scope）
    # 后续 scope 到位后可开启
    # for name in to_add:
    #     s = skills[name]
    #     lark_cli(["api", "POST", f"/open-apis/bitable/v1/apps/{BITABLE_APP}/tables/{BITABLE_TABLE}/records",
    #               "--as", "user", "--data", json.dumps({"fields": {"技能名称": name, **s}})])

if __name__ == "__main__":
    main()
