#!/Users/liyaohua/.nvm/versions/node/v22.22.0/bin/node
/**
 * send_diary_image.js
 * 将日记图片发送到财财飞书窗口
 * 用法: node send_diary_image.js <图片路径>
 */
const https = require('https');
const fs = require('fs');
const path = require('path');

const APP_ID = 'cli_a934dc5be7389bde';
const APP_SECRET = 'uumKVuaDwmJqRkRdQReVwctlpJkLmQSX';
const CHAT_ID = 'oc_672b6574c3477985a1a517f748d3dd4a';

function request(method, hostname, path, headers, body) {
  return new Promise((resolve, reject) => {
    const opts = { hostname, path, method, headers };
    const req = https.request(opts, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => {
        try { resolve(JSON.parse(d)); }
        catch (e) { reject(new Error(d)); }
      });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

async function getToken() {
  const r = await request('POST', 'open.feishu.cn',
    '/open-apis/auth/v3/tenant_access_token/internal',
    { 'Content-Type': 'application/json' },
    JSON.stringify({ app_id: APP_ID, app_secret: APP_SECRET })
  );
  if (!r.tenant_access_token) throw new Error('Failed to get token');
  return r.tenant_access_token;
}

async function uploadImage(token, filePath) {
  const boundary = '----DiaryImage' + Date.now();
  const filename = path.basename(filePath);
  const fileData = fs.readFileSync(filePath);

  const header = `--${boundary}\r\nContent-Disposition: form-data; name="image_type"; \r\n\r\nmessage\r\n`
               + `--${boundary}\r\nContent-Disposition: form-data; name="image"; filename="${filename}"\r\nContent-Type: image/png\r\n\r\n`;

  // Use base64 for simplicity
  const body = Buffer.concat([
    Buffer.from(header, 'utf8'),
    fileData,
    Buffer.from(`\r\n--${boundary}--`, 'utf8')
  ]);

  const r = await request('POST', 'open.feishu.cn',
    '/open-apis/im/v1/images',
    {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'multipart/form-data; boundary=' + boundary,
    },
    body
  );
  if (!r.data || !r.data.image_key) throw new Error('Upload failed: ' + JSON.stringify(r));
  return r.data.image_key;
}

async function sendImage(token, imageKey) {
  const postData = JSON.stringify({
    receive_id: CHAT_ID,
    msg_type: 'image',
    content: JSON.stringify({ image_key: imageKey })
  });
  const r = await request('POST', 'open.feishu.cn',
    '/open-apis/im/v1/messages?receive_id_type=chat_id',
    {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(postData)
    },
    postData
  );
  if (r.code !== 0) throw new Error('Send failed: ' + r.msg);
  return r;
}

async function main() {
  const imgPath = process.argv[2];
  if (!imgPath || !fs.existsSync(imgPath)) {
    console.error('❌ 图片文件不存在:', imgPath);
    process.exit(1);
  }

  console.log('🔐 获取 token...');
  const token = await getToken();

  console.log('📤 上传图片...');
  const imageKey = await uploadImage(token, imgPath);
  console.log('   image_key:', imageKey);

  console.log('📨 发送图片...');
  await sendImage(token, imageKey);
  console.log('✅ 发送成功');
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
