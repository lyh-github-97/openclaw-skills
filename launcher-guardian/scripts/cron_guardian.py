#!/usr/bin/env python3
"""
launcher-guardian: LaunchAgent 看护脚本
每日自动巡检 → 诊断 → 修复 → 重触发 → 推送报告
"""
import plistlib, os, glob, subprocess, re, sys
from datetime import datetime, date, timedelta

HOME = os.path.expanduser("~")
LOG_DIR = f"{HOME}/.openclaw/logs"
MEMORY_DIR = f"{HOME}/.openclaw/workspace/memory"
TARGET_CHAT = "oc_672b6574c3477985a1a517f748d3dd4a"

LAUNCHD_PREFIXES = ["ai.openclaw.", "com.openclaw.", "com.\u722a\u5df4."]
EXCLUDED = {"ai.openclaw.gateway"}

AGENTS = {
    "ai.openclaw.diary-full": {"log": "diary-full.log", "fix": "nvm_return"},
    "ai.openclaw.diary-collect": {"log": "diary-collect.log", "fix": "nvm_return"},
    "ai.openclaw.morningreport": {"log": "morning_report.log", "fix": "nvm_return"},
    "ai.openclaw.eveningreport": {"log": "evening_report.log", "fix": "nvm_return"},
    "ai.openclaw.skills-backup": {"log": "skills_backup.log", "fix": "nvm_return"},
    "ai.openclaw.memory-backup": {"log": "backup-memory.log", "fix": "nvm_return"},
    "ai.openclaw.deep-research": {"log": "deep-research.log", "fix": "nvm_return"},
    "ai.openclaw.spotlight-collect": {"log": "spotlight-collect.log", "fix": "nvm_return"},
    "ai.openclaw.ft-sync": {"log": "ft_to_feishu.log", "fix": "nvm_return"},
    "ai.openclaw.zlib-nightly": {"log": "zlib-nightly.log", "fix": "nvm_return"},
    "ai.openclaw.local-memory-curate": {"log": "local-memory-curate.log", "fix": "python_path"},
    "ai.openclaw.memory-archive": {"log": "memory-archive.log", "fix": "python_path"},
    "ai.openclaw.dashboard-fill": {"log": "dashboard-fill.log", "fix": "python_path"},
    "ai.openclaw.dashboard-check": {"log": "dashboard-check.log", "fix": "python_path"},
    "ai.openclaw.bb-browser": {"log": "bb-browser.log", "fix": "nvm_return"},
    "com.openclaw.ai-weekly-report": {"log": "ai-weekly-report.log", "fix": "nvm_return"},
    "com.openclaw.apiquota": {"log": "apiquota.log", "fix": "nvm_return"},
    "com.openclaw.backup": {"log": "backup.log", "fix": "nvm_return"},
    "com.openclaw.vpn-monitor": {"log": "vpn-monitor.log", "fix": "nvm_return"},
}

report_sections = {"normal": [], "fixed": [], "failed": []}

def run(cmd):
    r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True)
    return r.returncode, r.stdout

def get_launchctl_status(label):
    rc, out = run(f"launchctl list {label}")
    if rc != 0 or not out:
        return None, None
    for line in out.strip().split("\n"):
        line = line.strip()
        if line.startswith("PID"):
            try:
                pid = int(line.split("=")[-1].strip().rstrip(",;"))
            except:
                pid = None
        elif line.startswith("Status"):
            try:
                status = int(line.split("=")[-1].strip().rstrip(",;"))
            except:
                status = None
        else:
            pid, status = None, None
    return pid, status

def scan_log_errors(log_path):
    if not os.path.exists(log_path):
        return None
    with open(log_path) as f:
        content = f.read()
    errors = []
    all_lines = content.split("\n")
    # 只看最后 30 行，避免历史错误误报
    for line in all_lines[-30:]:
        stripped = line.strip()
        if not stripped:
            continue
        # 忽略无害标记行
        if stripped.startswith("· ") or stripped.startswith("#"):
            continue
        lower = stripped.lower()
        if any(kw in lower for kw in ["error", "traceback", "failed", "fatal", "crashed", "mismatched", "syntax error", "找不到", "no api key"]) and "[未知]" not in stripped:
            errors.append(stripped)
    return errors if errors else None

def detect_fix_mode(label, errors):
    if not errors:
        return None
    err_text = " ".join(errors).lower()
    if "mismatched tag" in err_text or "format error" in err_text:
        return "plist_xml"
    if "npmrc" in err_text or "nvm" in err_text or "return 11" in err_text:
        return "nvm_return"
    if "set -e" in err_text:
        return "nvm_return"
    if "找不到记忆文件" in err_text:
        return "memory_file"
    if "node" in err_text and ("not found" in err_text or "no such file" in err_text):
        return "node_path"
    if "python" in err_text and ("not found" in err_text or "no such file" in err_text):
        return "python_path"
    return None

def fix_nvm_in_shell(sh_path):
    """修复 nvm return 11：只在行首直接 source 的地方包子shell，已在子shell内的跳过"""
    if not os.path.exists(sh_path):
        return False, f"脚本不存在: {sh_path}"
    with open(sh_path) as f:
        lines = f.readlines()
    original = "".join(lines)
    fixed = False
    new_lines = []
    for line in lines:
        # 跳过已包在子shell里的
        if "( export NVM_DIR=" in line and "nvm.sh" in line:
            new_lines.append(line)
            continue
        stripped = line.lstrip()
        # 匹配直接 source nvm.sh 且没有 || true 保护的
        if re.search(r'^\s*\\[ -s .*nvm\.sh.*\\] && \\\\. .*nvm\.sh', line):
            newline = re.sub(
                r'(\[ -s "[^"]*nvm\.sh[^"]*"\] && \\\\. )("[^"]*nvm\.sh[^"]*")',
                r'( export NVM_DIR="$NVM_DIR"; \1\2 ) 2>/dev/null || true',
                line
            )
            new_lines.append(newline)
            fixed = True
            continue
        # 匹配裸 source，没有 || 保护
        if re.search(r'^\s*(?!\()[^|&]*\\\. .*nvm\.sh', line) and "||" not in line:
            newline = re.sub(
                r'(\\(\. )("[^"]*nvm\.sh[^"]*")',
                r'( export NVM_DIR="$NVM_DIR"; \1\2 ) 2>/dev/null || true',
                line
            )
            new_lines.append(newline)
            fixed = True
            continue
        new_lines.append(line)
    if not fixed:
        return False, "未找到需要修复的 nvm 加载代码"
    with open(sh_path, "w") as f:
        f.writelines(new_lines)
    return True, "nvm return 11 问题已隔离"

def fix_plist_xml(plist_path):
    try:
        data, err = read_plist(plist_path)
        if err:
            with open(plist_path) as f:
                content = f.read()
            # 修复 <key>XXX</integer> → <key>XXX</key><integer>
            fixed = re.sub(r'<key>(\w+)</integer>', r'<key>\1</key><integer>', content)
            with open(plist_path, "wb") as f:
                plistlib.dump(plistlib.loads(fixed), f)
            return True, "plist XML 标签修复"
    except Exception as e:
        return False, f"plist修复失败: {e}"
    return True, "plistlib 重序列化成功"

def read_plist(path):
    try:
        with open(path, "rb") as f:
            return plistlib.load(f), None
    except Exception as e:
        return None, str(e)

def ensure_memory_file():
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    path = f"{MEMORY_DIR}/{yesterday}.md"
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(f"# 记忆 {yesterday}\n\n")
        return True, f"已创建: {yesterday}.md"
    return False, "记忆文件已存在"

def reload_launchagent(label):
    run(f"launchctl bootout gui/{os.getuid()}/{label}")
    import time; time.sleep(1)
    plist = f"{HOME}/Library/LaunchAgents/{label}.plist"
    rc2, err = run(f"launchctl load {plist}")
    if rc2 == 0:
        return True, f"✅ 已重新加载 {label}"
    return False, f"❌ 加载失败: {err[:100]}"

def send_feishu_report(report_text):
    """通过飞书机器人发文字报告到财财窗口"""
    try:
        import urllib.request, json
        
        # 读取飞书凭证
        try:
            app_id = subprocess.run(
                [sys.executable, "-c",
                 f"import json; d=json.load(open('{HOME}/.openclaw/openclaw.json')); print(d.get('plugins',{{}}).get('feishu',{{}}).get('appId',''))"],
                capture_output=True, text=True
            ).stdout.strip()
            app_secret = subprocess.run(
                [sys.executable, "-c",
                 f"import json; d=json.load(open('{HOME}/.openclaw/openclaw.json')); print(d.get('plugins',{{}}).get('feishu',{{}}).get('appSecret',''))"],
                capture_output=True, text=True
            ).stdout.strip()
        except:
            app_id, app_secret = "", ""
        
        if not app_id or not app_secret:
            print("  ⚠️ 无法获取飞书凭证，跳过推送")
            return
        
        # 获取 token
        req = urllib.request.Request(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            data=json.dumps({"app_id": app_id, "app_secret": app_secret}).encode(),
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=10)
        token_data = json.loads(resp.read())
        token = token_data.get("tenant_access_token", "")
        
        if not token:
            print("  ⚠️ 获取 tenant token 失败")
            return
        
        # 发送消息
        send_url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
        msg_data = {
            "receive_id": TARGET_CHAT,
            "msg_type": "text",
            "content": json.dumps({"text": report_text})
        }
        req2 = urllib.request.Request(
            send_url,
            data=json.dumps(msg_data).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        )
        resp2 = urllib.request.urlopen(req2, timeout=10)
        result = json.loads(resp2.read())
        if result.get("code") == 0:
            print("  ✅ 报告已发送至财财窗口")
        else:
            print(f"  ⚠️ 发送失败: {result.get('msg')}")
    except Exception as e:
        print(f"  ⚠️ 飞书推送异常: {e}")

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] 🔍 LaunchAgent 巡检开始...")
    
    all_labels = []
    for prefix in LAUNCHD_PREFIXES:
        for f in glob.glob(f"{HOME}/Library/LaunchAgents/{prefix}*.plist"):
            label = os.path.basename(f).replace(".plist", "")
            if label not in EXCLUDED:
                all_labels.append(label)
    all_labels = sorted(set(all_labels))
    print(f"   共巡检 {len(all_labels)} 个")
    
    for label in all_labels:
        pid, status = get_launchctl_status(label)
        cfg = AGENTS.get(label, {})
        log_name = cfg.get("log", f"{label.replace('.','-')}.log")
        log_path = f"{LOG_DIR}/{log_name}"
        errors = scan_log_errors(log_path)
        fix_mode = cfg.get("fix")
        
        is_issue = (status is not None and status != 0) or (errors is not None)
        
        if not is_issue:
            report_sections["normal"].append(label)
            continue
        
        print(f"\n  ⚠️  {label}: status={status}, errors={len(errors) if errors else 0}")
        if errors:
            for e in errors[:3]:
                print(f"     {e[:120]}")
        
        detected = detect_fix_mode(label, errors) if errors else None
        
        if not detected:
            report_sections["failed"].append(
                f"**{label}**：日志有错误但无法识别模式，样例: {errors[0][:80] if errors else 'N/A'}"
            )
            print(f"     ❌ 未能识别问题模式")
            continue
        
        fixed = False
        fix_msg = ""
        reload_msg = ""
        
        if detected == "nvm_return":
            plist_path = f"{HOME}/Library/LaunchAgents/{label}.plist"
            data, _ = read_plist(plist_path)
            sh_path = None
            if data:
                for a in data.get("ProgramArguments", []):
                    if isinstance(a, str) and a.endswith(".sh"):
                        sh_path = a
                        break
            if sh_path:
                fixed, fix_msg = fix_nvm_in_shell(sh_path)
        
        elif detected == "plist_xml":
            plist_path = f"{HOME}/Library/LaunchAgents/{label}.plist"
            fixed, fix_msg = fix_plist_xml(plist_path)
        
        elif detected == "memory_file":
            fixed, fix_msg = ensure_memory_file()
        
        elif detected in ("node_path", "python_path"):
            plist_path = f"{HOME}/Library/LaunchAgents/{label}.plist"
            data, _ = read_plist(plist_path)
            if data:
                for a in data.get("ProgramArguments", []):
                    if isinstance(a, str) and a.endswith(".sh"):
                        if "PYTHON_PATH" not in open(a).read():
                            with open(a) as f:
                                content = f.read()
                            if "export PATH=" in content and "/python3" not in content:
                                lines = content.split("\n")
                                new_lines = []
                                py_inserted = False
                                for ln in lines:
                                    new_lines.append(ln)
                                    if not py_inserted and ln.startswith("export PATH="):
                                        new_lines.append(
                                            'export PYTHON_PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"'
                                        )
                                        py_inserted = True
                                with open(a, "w") as f:
                                    f.write("\n".join(new_lines))
                                fixed = True
                                fix_msg = "PATH 修复完成"
                        break
        
        if fixed:
            ok, reload_msg = reload_launchagent(label)
            report_sections["fixed"].append(
                f"**{label}**：{fix_msg} → {reload_msg}"
            )
            print(f"     ✅ 修复: {fix_msg} → {reload_msg}")
        else:
            report_sections["failed"].append(
                f"**{label}**：检测到 {detected} 但修复失败，错误: {fix_msg or errors[0][:60] if errors else 'N/A'}"
            )
            print(f"     ❌ 修复失败: {fix_msg}")
    
    # 生成报告
    total = len(all_labels)
    fixed_n = len(report_sections["fixed"])
    failed_n = len(report_sections["failed"])
    normal_n = len(report_sections["normal"])
    
    report_lines = [
        f"## ⚙️ LaunchAgent 巡检报告 | {now}\n",
        f"共巡检 **{total}** 个，正常 **{normal_n}** 个，修复 **{fixed_n}** 个，未解决 **{failed_n}** 个\n",
    ]
    
    if report_sections["normal"]:
        report_lines.append(f"✅ **正常**（{normal_n}个）")
        for a in report_sections["normal"]:
            report_lines.append(f"- {a}")
        report_lines.append("")
    
    if report_sections["fixed"]:
        report_lines.append(f"🔧 **已修复**（{fixed_n}个）")
        for item in report_sections["fixed"]:
            report_lines.append(f"- {item}")
        report_lines.append("")
    
    if report_sections["failed"]:
        report_lines.append(f"❌ **未解决**（{failed_n}个）")
        for item in report_sections["failed"]:
            report_lines.append(f"- {item}")
        report_lines.append("")
    
    report_text = "\n".join(report_lines)
    print(f"\n{report_text}")
    
    if fixed_n > 0 or failed_n > 0:
        send_feishu_report(report_text)
    
    print(f"\n✅ 完成: 修复{fixed_n}，失败{failed_n}，正常{normal_n}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
