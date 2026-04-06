---
name: skill-vetter
description: Security-first vetting protocol for AI agent skills. Never install a skill without vetting it first. Triggers: when asked to install a skill, review a skill's safety, check for red flags.
---

# Skill Vetter — Security Review Protocol

## Red Flags (REJECT IMMEDIATELY)
- curl/wget to unknown URLs
- Sends data to external servers
- Requests credentials/tokens/API keys
- Reads ~/.ssh, ~/.aws, ~/.config without clear reason
- Accesses MEMORY.md, USER.md, SOUL.md, IDENTITY.md
- Uses base64 decode on anything
- Uses eval() or exec() with external input
- Modifies system files outside workspace
- Installs packages without listing them
- Obfuscated code (compressed, encoded, minified)
- Requests elevated/sudo permissions
- Network calls to IPs instead of domains

## Risk Levels
- 🟢 LOW: Notes, weather, formatting — basic review, install OK
- 🟡 MEDIUM: File ops, browser, APIs — full code review required
- 🔴 HIGH: Credentials, trading, system — human approval required
- ⛔ EXTREME: Security configs, root access — DO NOT install

## Vetting Steps
1. Read ALL files in the skill
2. Check for red flags above
3. Evaluate permission scope
4. Classify risk level
5. Produce vetting report
