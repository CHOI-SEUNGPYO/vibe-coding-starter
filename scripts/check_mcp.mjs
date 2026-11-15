// End-to-end MCP checks. Requires npm ci; never reads account credentials.
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { createInterface } from 'node:readline';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const protocolVersion = '2025-03-26';
const initialize = { protocolVersion, capabilities: {}, clientInfo: { name: 'vibe-smoke-check', version: '1.0.0' } };
const mode = process.argv[2] ?? 'all';
if (!['all', 'docs', 'browser'].includes(mode)) {
  console.error('Usage: node scripts/check_mcp.mjs [all|docs|browser]');
  process.exit(2);
}

function unpack(text) {
  try { return JSON.parse(text); } catch {}
  const records = text.split(/\r?\n/).filter(line => line.startsWith('data:'));
  for (const line of records.reverse()) {
    try { const value = JSON.parse(line.slice(5).trim()); if ('result' in value || 'error' in value) return value; } catch {}
  }
  throw new Error('No JSON-RPC result in response');
}

async function docsCheck() {
  const url = 'https://developers.openai.com/mcp';
  let session;
  let id = 0;
  async function rpc(method, params, notification = false) {
    const headers = { 'content-type': 'application/json', accept: 'application/json, text/event-stream', 'MCP-Protocol-Version': protocolVersion };
    if (session) headers['Mcp-Session-Id'] = session;
    const body = { jsonrpc: '2.0', method, params };
    if (!notification) body.id = ++id;
    const response = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body), signal: AbortSignal.timeout(45000) });
    if (!response.ok) throw new Error(`Docs MCP HTTP ${response.status}`);
    session = response.headers.get('mcp-session-id') ?? session;
    if (notification || response.status === 202) return;
    const message = unpack(await response.text());
    if (message.error) throw new Error(`Docs MCP: ${message.error.message}`);
    return message.result;
  }
  await rpc('initialize', initialize);
  await rpc('notifications/initialized', {}, true);
  const listed = await rpc('tools/list', {});
  const search = listed.tools?.find(tool => /search.*openai|search/i.test(tool.name) && tool.inputSchema?.properties?.query);
  if (!search) throw new Error('Docs MCP did not expose a documentation search tool');
  const result = await rpc('tools/call', { name: search.name, arguments: { query: 'Codex AGENTS.md' } });
  if (result.isError || !result.content?.length) throw new Error('Docs MCP search failed or returned no content');
  console.log(`PASS openai-docs: initialize, ${listed.tools.length} tools, ${search.name} response`);
}

async function browserCheck() {
  const server = createServer((_request, response) => {
    response.setHeader('content-type', 'text/html; charset=utf-8');
    response.end('<!doctype html><html lang="en"><title>Vibe MCP smoke test</title><main><h1>VIBE_MCP_OK</h1><button onclick="this.textContent=\'Clicked\'">Test button</button></main></html>');
  });
  await new Promise((done, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', done); });
  const child = spawn(process.execPath, [resolve(root, 'node_modules/@playwright/mcp/cli.js'), '--browser', 'chromium', '--headless', '--isolated'], { cwd: root, stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
  const waiting = new Map();
  let sequence = 0;
  let stderr = '';
  child.stderr.on('data', value => { stderr = (stderr + value).slice(-2000); });
  const lines = createInterface({ input: child.stdout });
  const failPending = error => { for (const entry of waiting.values()) { clearTimeout(entry.timer); entry.reject(error); } waiting.clear(); };
  child.on('error', failPending);
  child.on('exit', code => failPending(new Error(`Playwright MCP exited (${code}): ${stderr}`)));
  lines.on('line', line => {
    let message; try { message = JSON.parse(line); } catch { return; }
    const entry = waiting.get(message.id);
    if (!entry) return;
    waiting.delete(message.id); clearTimeout(entry.timer);
    if (message.error) entry.reject(new Error(message.error.message)); else entry.resolve(message.result);
  });
  async function rpc(method, params, timeoutMs = 60000) {
    const id = ++sequence;
    return new Promise((resolveResult, reject) => {
      const timer = setTimeout(() => { waiting.delete(id); reject(new Error(`Playwright MCP timeout: ${method}`)); }, timeoutMs);
      waiting.set(id, { resolve: resolveResult, reject, timer });
      child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
    });
  }
  async function snapshotText(result) {
    if (result.isError) throw new Error(`Browser tool returned an error: ${JSON.stringify(result.content)}`);
    const text = (result.content ?? []).filter(item => item.type === 'text').map(item => item.text).join('\n');
    const linked = text.match(/\[Snapshot\]\(([^)]+)\)/)?.[1];
    if (!linked) return text;
    const normalized = linked.replaceAll('\\', '/');
    if (!/^\.playwright-mcp\/[^/]+\.yml$/.test(normalized)) throw new Error('Unexpected browser snapshot path');
    return await readFile(resolve(root, normalized), 'utf8');
  }
  try {
    await rpc('initialize', initialize);
    child.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized', params: {} }) + '\n');
    const listed = await rpc('tools/list', {});
    if (!listed.tools?.some(tool => tool.name === 'browser_navigate')) throw new Error('browser_navigate missing');
    const result = await rpc('tools/call', { name: 'browser_navigate', arguments: { url: `http://127.0.0.1:${server.address().port}/` } });
    const snapshot = await snapshotText(result);
    if (!snapshot.includes('VIBE_MCP_OK')) throw new Error('Browser did not render the test page');
    const ref = snapshot.match(/button "Test button" \[ref=([^\]]+)\]/)?.[1];
    if (!ref) throw new Error('Test button missing from browser accessibility snapshot');
    const clicked = await rpc('tools/call', { name: 'browser_click', arguments: { target: ref } });
    if (!(await snapshotText(clicked)).includes('Clicked')) throw new Error('Browser button click did not update the page');
    console.log(`PASS playwright: initialize, ${listed.tools.length} tools, Chromium navigation and button click`);
  } finally {
    if (child.exitCode === null && !child.killed) {
      await rpc('tools/call', { name: 'browser_close', arguments: {} }, 5000).catch(() => {});
    }
    child.stdin.end(); child.kill(); lines.close(); failPending(new Error('MCP check ended'));
    await new Promise(done => server.close(done));
  }
}

try {
  if (mode !== 'browser') await docsCheck();
  if (mode !== 'docs') await browserCheck();
} catch (error) {
  console.error(`FAIL ${error.message}`);
  process.exitCode = 1;
}
