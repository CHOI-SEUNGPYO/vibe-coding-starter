import test from 'node:test';
import assert from 'node:assert/strict';
import { context7Check, httpRpc } from '../scripts/check_mcp.mjs';

const textResult = text => ({ content: [{ type: 'text', text }] });
const tools = [
  { name: 'resolve-library-id', inputSchema: { properties: { libraryName: { type: 'string' }, query: { type: 'string' } } } },
  { name: 'query-docs', inputSchema: { properties: { libraryId: { type: 'string' }, query: { type: 'string' }, language: { type: 'string' } } } },
];

function responder({ resolved = textResult('- Context7-compatible library ID: /websites/fastapi_tiangolo'), queried = textResult('Source: https://fastapi.tiangolo.com/tutorial/body/\nclass Item(BaseModel):\n    name: str') } = {}) {
  const calls = [];
  const rpc = async (method, params) => {
    calls.push({ method, params });
    if (method === 'tools/list') return { tools };
    if (method === 'tools/call') return params.name === 'resolve-library-id' ? resolved : queried;
    return {};
  };
  return { rpc, calls };
}

test('Context7 requires successful resolution and a sourced documentation query', async () => {
  const { rpc, calls } = responder();
  await context7Check(rpc);
  const toolCalls = calls.filter(call => call.method === 'tools/call');
  assert.deepEqual(toolCalls.map(call => call.params.name), ['resolve-library-id', 'query-docs']);
  assert.equal(toolCalls[1].params.arguments.libraryId, '/websites/fastapi_tiangolo');
});

test('Context7 does not query a third-party library when the official match is absent', async () => {
  const { rpc, calls } = responder({ resolved: textResult('- Context7-compatible library ID: /somewhere/unrelated') });
  await assert.rejects(context7Check(rpc), /official FastAPI/);
  assert.equal(calls.filter(call => call.method === 'tools/call').length, 1);
});

for (const [description, queried] of [
  ['tool error', { ...textResult('Source: https://fastapi.tiangolo.com/tutorial/body/ BaseModel'), isError: true }],
  ['empty content', { content: [] }],
  ['no official source', textResult('FastAPI BaseModel example with no source')],
  ['lookalike source', textResult('BaseModel https://fastapi.tiangolo.com.example.org/tutorial/body/')],
]) {
  test(`Context7 rejects ${description}`, async () => {
    await assert.rejects(context7Check(responder({ queried }).rpc), /Context7/);
  });
}

for (const status of [401, 403, 429]) {
  test(`HTTP ${status} fails with the server name`, async () => {
    const rpc = httpRpc('Context7', 'https://mcp.context7.com/mcp', async () => new Response('', { status }));
    await assert.rejects(rpc('initialize', {}), new RegExp(`Context7 MCP HTTP ${status}`));
  });
}

test('transport failures remain failures', async () => {
  const rpc = httpRpc('Context7', 'https://mcp.context7.com/mcp', async () => { throw new Error('offline'); });
  await assert.rejects(rpc('initialize', {}), /Context7 MCP transport failed: offline/);
});

test('malformed HTTP responses fail with the server name', async () => {
  const rpc = httpRpc('Context7', 'https://mcp.context7.com/mcp', async () => new Response('not JSON-RPC'));
  await assert.rejects(rpc('initialize', {}), /Context7 MCP response failed/);
});
