#!/usr/bin/env python3
"""
Portfolio Tracker - 持仓管理脚本
管理 ~/.openclaw/workspace-research/catalyst_scanner/portfolio.json
"""
import json
import sys
import os
from datetime import datetime

PORTFOLIO_FILE = os.path.expanduser("~/.openclaw/workspace-research/catalyst_scanner/portfolio.json")

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return {"positions": {}, "last_updated": None, "history": []}

def save_portfolio(data):
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_position(code, name, cost, shares, note=""):
    """更新单个持仓"""
    data = load_portfolio()
    data["positions"][code] = {
        "name": name,
        "cost": float(cost),
        "shares": int(shares),
        "note": note,
        "updated": datetime.now().strftime("%Y-%m-%d")
    }
    save_portfolio(data)
    return data["positions"][code]

def remove_position(code):
    """删除持仓"""
    data = load_portfolio()
    if code in data["positions"]:
        del data["positions"][code]
        save_portfolio(data)
        return True
    return False

def get_portfolio():
    """获取当前持仓"""
    return load_portfolio()

def format_portfolio():
    """格式化输出持仓"""
    data = load_portfolio()
    if not data["positions"]:
        return "暂无持仓记录"
    
    lines = []
    for code, info in data["positions"].items():
        lines.append(f"{code} {info['name']}: 成本={info['cost']:.2f}, 股数={info['shares']}, 更新={info['updated']}")
        if info.get("note"):
            lines.append(f"  备注: {info['note']}")
    return "\n".join(lines)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    
    if cmd == "show":
        print(format_portfolio())
    elif cmd == "get":
        import json
        print(json.dumps(get_portfolio(), ensure_ascii=False, indent=2))
    elif cmd == "update" and len(sys.argv) >= 6:
        # python3 portfolio_manager.py update 000818 航锦科技 21.78 100
        code, name, cost, shares = sys.argv[2], sys.argv[3], float(sys.argv[4]), int(sys.argv[5])
        note = sys.argv[6] if len(sys.argv) > 6 else ""
        result = update_position(code, name, cost, shares, note)
        print(f"已更新: {code} {name}")
    elif cmd == "remove" and len(sys.argv) >= 3:
        code = sys.argv[2]
        if remove_position(code):
            print(f"已删除: {code}")
        else:
            print(f"未找到: {code}")
    else:
        print("用法: portfolio_manager.py [show|get|update|remove]")
        print("  show                      - 显示持仓")
        print("  get                       - JSON格式获取持仓")
        print("  update <code> <name> <cost> <shares> [note] - 更新持仓")
        print("  remove <code>            - 删除持仓")
