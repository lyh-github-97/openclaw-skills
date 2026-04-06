#!/Users/liyaohua/.nvm/versions/node/v22.22.0/bin/node
/**
 * send_to_finance.js
 * 向财财机器人发送日报（直接 API）
 * 用法: node send_to_finance.js <报告文件路径>
 */
const https = require('https');
const fs = require('fs');

const FINANCE_APP_ID = 'cli_a934dc5be7389bde';
const FINANCE_APP_SECRET = 'uumKVuaDwmJqRkRdQReVwctlpJkLmQSX';
const CHAT_ID = 'oc_672b6574c3477985a1a517f748d3dd4a';

function getToken() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ app_id: FINANCE_APP_ID, app_secret: FINANCE_APP_SECRET });
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

function sendMessage(token, text) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({
      receive_id: CHAT_ID,
      msg_type: 'text',
      content: JSON.stringify({ text })
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
  const reportFile = process.argv[2];
  if (!reportFile) {
    console.error('用法: node send_to_finance.js <报告文件路径>');
    process.exit(1);
  }
  if (!fs.existsSync(reportFile)) {
    console.error('报告文件不存在:', reportFile);
    process.exit(1);
  }

  const content = fs.readFileSync(reportFile, 'utf8');
  // 拒发模板内容（未经过LLM生成）
  const templateMarkers = ['请根据以下今日', '请按以下结构输出', '【今日市场一句话】', '你是一个专业的'];
  if (templateMarkers.some(m => content.includes(m))) {
    console.error('❌ 拒绝发送：检测到模板内容，请先生成报告。');
    process.exit(1);
  }
  if (content.length < 100) {
    console.error('报告文件内容过少（<100字节），跳过发送:', content.length);
    process.exit(1);
  }

  const token = await getToken();
  const result = await sendMessage(token, content);
  if (result.code === 0) {
    console.log('✅ 发送成功');
  } else {
    console.error('❌ 发送失败:', result.code, result.msg);
    process.exit(1);
  }
}

main().catch(e => { console.error(e); process.exit(1); });
