#!/Users/liyaohua/.nvm/versions/node/v22.22.0/bin/node
/**
 * send_finance_report_card.js
 * 向财财发送飞书富文本卡片（interactive card）
 * 用法: node send_finance_report_card.js <report_file>
 */
const https = require('https');
const fs = require('fs');

const APP_ID = 'cli_a934dc5be7389bde';
const APP_SECRET = 'uumKVuaDwmJqRkRdQReVwctlpJkLmQSX';
const CHAT_ID = 'oc_672b6574c3477985a1a517f748d3dd4a';

function getToken() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ app_id: APP_ID, app_secret: APP_SECRET });
    const req = https.request({
      hostname: 'open.feishu.cn',
      path: '/open-apis/auth/v3/tenant_access_token/internal',
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) }
    }, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => {
        try { resolve(JSON.parse(d).tenant_access_token); }
        catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(data); req.end();
  });
}

function escape(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function mdToFeishu(text) {
  let result = text;

  // 分割线
  result = result.replace(/^---$/gm, '<hr/>');

  // h1/h2/h3 标题层级（数字越大字体越小）
  result = result.replace(/^### (.+)$/gm, '<h5>$1</h5>');
  result = result.replace(/^## (.+)$/gm, '<h4>$1</h4>');
  result = result.replace(/^# (.+)$/gm, '<h3>$1</h3>');

  // 分割线标题（如━━━ 📈 大盘 ━━━）→ 加粗小标题
  result = result.replace(
    /^(━━━[^━]+━━━)$/gm,
    '<strong><h5>$1</h5></strong>'
  );

  // 关键结论行加绿/红色标注（【一句话结论】【外围指引】等）
  result = result.replace(
    /^【一句话结论】(.+)$/gm,
    '<p><font color="#34A853"><strong>【结论】</strong></font> $1</p>'
  );
  result = result.replace(
    /^【外围指引】(.+)$/gm,
    '<p><font color="#34A853"><strong>【外围指引】</strong></font> $1</p>'
  );
  result = result.replace(
    /^【大盘】(.+)$/gm,
    '<p><font color="#34A853"><strong>【大盘】</strong></font> $1</p>'
  );
  // 风险行加红色
  result = result.replace(
    /^→ 风险[：:](.+)$/gm,
    '<p><font color="#EA4335"><strong>→ 风险</strong></font>: $1</p>'
  );
  // 推荐/操作建议加绿色
  result = result.replace(
    /^→ (推荐理由|波段目标|操作建议)[：:](.+)$/gm,
    '<p><font color="#34A853"><strong>→ $1</strong></font>: $2</p>'
  );

  // 加粗 **text** → <strong>text</strong>
  result = result.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // 斜体 *text* → <em>text</em>
  result = result.replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, '<em>$1</em>');

  // 代码
  result = result.replace(/`([^`]+)`/g, '<code>$1</code>');

  // 图片 → 忽略
  result = result.replace(/!\[.*?\]\(.*?\)/g, '');

  // 超链接 → 纯文本
  result = result.replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1');

  // 列表项优化（加粗编号）
  result = result.replace(/^① (.+)$/gm, '<p><strong>①</strong> $1</p>');
  result = result.replace(/^② (.+)$/gm, '<p><strong>②</strong> $1</p>');
  result = result.replace(/^③ (.+)$/gm, '<p><strong>③</strong> $1</p>');
  result = result.replace(/^• (.+)$/gm, '<p>• $1</p>');

  // 多重换行压缩
  result = result.replace(/\n{3,}/g, '\n\n');

  return result.trim();
}

function sendCard(token, markdown) {
  const elements = [
    {
      tag: 'markdown',
      content: mdToFeishu(markdown),
      text_align: 'left'
    }
  ];
  
  const card = {
    config: { wide_screen_mode: true },
    header: {
      template: 'purple',
      title: { content: '📊 财经晚报 · ' + new Date().toLocaleDateString('zh-CN', {year:'numeric',month:'2-digit',day:'2-digit'}), tag: 'plain_text' }
    },
    elements
  };
  
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({
      receive_id: CHAT_ID,
      msg_type: 'interactive',
      content: JSON.stringify(card)
    });
    const req = https.request({
      hostname: 'open.feishu.cn',
      path: '/open-apis/im/v1/messages?receive_id_type=chat_id',
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    }, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => {
        try { resolve(JSON.parse(d)); }
        catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(postData); req.end();
  });
}

async function main() {
  const reportFile = process.argv[2] || '/tmp/daily_report.md';
  if (!fs.existsSync(reportFile)) {
    console.error('报告文件不存在:', reportFile);
    process.exit(1);
  }
  
  const report = fs.readFileSync(reportFile, 'utf8');
  if (report.trim().length < 50) {
    console.error('报告内容过短，跳过发送');
    process.exit(1);
  }
  
  const token = await getToken();
  const result = await sendCard(token, report);
  
  if (result.code === 0) {
    console.log('发送成功:', result.msg);
  } else {
    console.error('发送失败:', result.code, result.msg);
    process.exit(1);
  }
}

main().catch(e => { console.error(e); process.exit(1); });
