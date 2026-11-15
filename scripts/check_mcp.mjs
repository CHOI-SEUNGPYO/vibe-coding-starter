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

function unpack(text) {
  try { return JSON.parse(text); } catch {}
  const records = text.split(/\r?\n/).filter(line => line.startsWith('data:'));
  for (const line of records.reverse()) {
    try { const value = JSON.parse(line.slice(5).trim()); if ('result' in value || 'error' in value) return value; } catch {}
  }
  throw new Error('No JSON-RPC result in response');
}

export function httpRpc(label, url, fetcher = fetch) {
  let session;
  let id = 0;
  let negotiatedVersion = protocolVersion;
  return async function rpc(method, params, notification = false) {
    const headers = { 'content-type': 'application/json', accept: 'application/json, text/event-stream', 'MCP-Protocol-Version': negotiatedVersion };
    if (session) headers['Mcp-Session-Id'] = session;
    const body = { jsonrpc: '2.0', method, params };
    if (!notification) body.id = ++id;
    let response;
    try {
      response = await fetcher(url, { method: 'POST', headers, body: JSON.stringify(body), signal: AbortSignal.timeout(45000) });
    } catch (error) {
      throw new Error(`${label} MCP transport failed: ${error.message}`);
    }
    if (!response.ok) throw new Error(`${label} MCP HTTP ${response.status}${response.status === 429 ? ' (rate limit)' : [401, 403].includes(response.status) ? ' (authentication/access denied)' : ''}`);
    session = response.headers.get('mcp-session-id') ?? session;
    if (notification || response.status === 202) return;
    let message;
    try { message = unpack(await response.text()); } catch (error) {
      throw new Error(`${label} MCP response failed: ${error.message}`);
    }
    if (message.error) throw new Error(`${label} MCP: ${message.error.message}`);
    if (!message.result || typeof message.result !== 'object') throw new Error(`${label} MCP returned no result`);
    if (method === 'initialize' && message.result.protocolVersion) negotiatedVersion = message.result.protocolVersion;
    return message.result;
  };
}

async function docsCheck() {
  const rpc = httpRpc('OpenAI Docs', 'https://developers.openai.com/mcp');
  await rpc('initialize', initialize);
  await rpc('notifications/initialized', {}, true);
  const listed = await rpc('tools/list', {});
  const search = listed.tools?.find(tool => /search.*openai|search/i.test(tool.name) && tool.inputSchema?.properties?.query);
  if (!search) throw new Error('Docs MCP did not expose a documentation search tool');
  const result = await rpc('tools/call', { name: search.name, arguments: { query: 'Codex AGENTS.md' } });
  if (result.isError || !result.content?.length) throw new Error('Docs MCP search failed or returned no content');
  console.log(`PASS openai-docs: initialize, ${listed.tools.length} tools, ${search.name} response`);
}

function toolText(result, name) {
  const text = (result?.content ?? []).filter(item => item.type === 'text').map(item => item.text).join('\n').trim();
  if (result?.isError || !text) throw new Error(`Context7 ${name} failed or returned no text`);
  return text;
}

export async function context7Check(rpc = httpRpc('Context7', 'https://mcp.context7.com/mcp')) {
  await rpc('initialize', initialize);
  await rpc('notifications/initialized', {}, true);
  const listed = await rpc('tools/list', {});
  for (const [name, required] of [['resolve-library-id', ['libraryName', 'query']], ['query-docs', ['libraryId', 'query']]]) {
    const tool = listed.tools?.find(item => item.name === name);
    if (!tool || !required.every(key => tool.inputSchema?.properties?.[key]?.type === 'string')) {
      throw new Error(`Context7 ${name} tool/schema missing`);
    }
  }
  const libraries = toolText(await rpc('tools/call', {
    name: 'resolve-library-id',
    arguments: { libraryName: 'FastAPI', query: 'Python FastAPI official documentation: declare a request body with Pydantic BaseModel in a POST endpoint.' },
  }), 'resolve-library-id');
  // Select the official documentation match returned by the resolver, not a third-party tutorial.
  const libraryId = '/websites/fastapi_tiangolo';
  if (!libraries.split(/\r?\n/).some(line => /Context7-compatible library ID:/.test(line) && line.split('Context7-compatible library ID:')[1].trim() === libraryId)) {
    throw new Error('Context7 did not resolve the official FastAPI documentation library');
  }
  const documentation = toolText(await rpc('tools/call', {
    name: 'query-docs',
    arguments: { libraryId, query: 'How do I declare a JSON request body with a Pydantic BaseModel in a FastAPI POST endpoint? Include a minimal official example.', language: 'Python' },
  }), 'query-docs');
  if (!/https:\/\/fastapi\.tiangolo\.com\//.test(documentation) || !/\bBaseModel\b/.test(documentation)) {
    throw new Error('Context7 query-docs returned no request-body example with an official FastAPI source');
  }
  console.log(`PASS context7: initialize, ${listed.tools.length} tools, resolve-library-id and query-docs with an official FastAPI source`);
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

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const mode = process.argv[2] ?? 'all';
  if (!['all', 'docs', 'context7', 'browser'].includes(mode)) {
    console.error('Usage: node scripts/check_mcp.mjs [all|docs|context7|browser]');
    process.exitCode = 2;
  } else {
    try {
      if (['all', 'docs'].includes(mode)) await docsCheck();
      if (['all', 'context7'].includes(mode)) await context7Check();
      if (['all', 'browser'].includes(mode)) await browserCheck();
    } catch (error) {
      console.error(`FAIL ${error.message}`);
      if (/Context7|OpenAI Docs|Docs MCP/.test(error.message)) {
        console.error('문서 MCP 연결 실패 시 공식 문서를 직접 확인하세요. 연결 검증은 실패 상태로 남습니다. docs/mcp.md 참고.');
      }
      process.exitCode = 1;
    }
  }
}
