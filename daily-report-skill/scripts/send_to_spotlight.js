#!/Users/liyaohua/.nvm/versions/node/v22.22.0/bin/node
/**
 * send_to_spotlight.js
 * 向探照灯会话发送日报
 * 用法: node send_to_spotlight.js <chat_id> <报告文件路径>
 */
const https = require('https');
const fs = require('fs');

const SPOTLIGHT_APP_ID = 'cli_a948b11aeb395cc9';
const SPOTLIGHT_APP_SECRET = 'SAdLA9dDRHdWznuQHKCMrf51gI2CuAo4';

function getToken() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ app_id: SPOTLIGHT_APP_ID, app_secret: SPOTLIGHT_APP_SECRET });
    const req = https.request({
      hostname: 'open.feishu.cn',
      path: '/open-apis/auth/v3/tenant_access_token/internal',
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) }
    }, res => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => {
        const d = JSON.parse(body);
        resolve(d.tenant_access_token);
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function sendMessage(token, chatId, content) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      receive_id: chatId,
      msg_type: 'text',
      content: JSON.stringify({ text: content })
    });
    const req = https.request({
      hostname: 'open.feishu.cn',
      path: '/open-apis/im/v1/messages?receive_id_type=chat_id',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    }, res => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => {
        const d = JSON.parse(body);
        if (d.code === 0) {
          console.log('✅ 发送成功');
          resolve();
        } else {
          console.log('❌ 发送失败:', d.msg);
          reject(new Error(d.msg));
        }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function main() {
  const chatId = process.argv[2];
  const reportFile = process.argv[3];
  if (!chatId || !reportFile) {
    console.error('用法: node send_to_spotlight.js <chat_id> <报告文件路径>');
    process.exit(1);
  }
  if (!fs.existsSync(reportFile)) {
    console.error('报告文件不存在:', reportFile);
    process.exit(1);
  }

  let report = fs.readFileSync(reportFile, 'utf-8');
  if (report.length < 100) {
    console.error('报告文件内容过少（<100字节），跳过发送');
    process.exit(1);
  }

  // 提取正文
  const contentStart = report.indexOf('---');
  report = contentStart >= 0 ? report.substring(contentStart) : report;

  // 清理无效链接（"待补充"、"（）"括号文本、非http链接）
  report = report
    .replace(/\[链接[：:]\s*https?:\/\/[^】\n]*(?:待补充|（[^）]*）)[^\n]*\n?/g, '')
    .replace(/https?:\/\/[^\s\n]*(?:待补充|（[^）]*）)/g, '')
    .replace(/\[链接[：:]\s*\n?/g, '[链接: ');

  // 截断超长内容（飞书text限制4096字符）
  if (report.length > 4000) {
    console.log(`⚠️ 报告过长(${report.length}字符)，截断至4000`);
    report = report.substring(0, 4000) + '\n\n...（内容过长已截断）';
  }

  const token = await getToken();
  await sendMessage(token, chatId, report);
}

main().catch(e => { console.error(e); process.exit(1); });
