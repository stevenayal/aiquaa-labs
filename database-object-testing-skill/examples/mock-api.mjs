import { createServer } from 'node:http';

export function createMockApi(role = 'baseline') {
  return createServer(async (request, response) => {
    const chunks = [];
    for await (const chunk of request) chunks.push(chunk);
    const body = chunks.length ? JSON.parse(Buffer.concat(chunks).toString('utf8')) : {};
    response.setHeader('content-type', 'application/json');
    if (request.headers.authorization !== 'Bearer local-example-token') {
      response.statusCode = 401;
      response.end(JSON.stringify({ error: { code: 'UNAUTHORIZED' } }));
      return;
    }
    if (request.url === '/v1/database/execute') {
      response.end(JSON.stringify({
        data: { rows: [{ customerId: body.arguments?.customerId, status: 'ACTIVE' }], rowCount: 1, out: { status: 'ACTIVE' } },
        metrics: { elapsedMs: role === 'candidate' ? 11 : 10 }
      }));
      return;
    }
    if (request.url === '/v1/database/explain') {
      response.end(JSON.stringify({ cost: role === 'candidate' ? 105 : 100, logicalReads: role === 'candidate' ? 9 : 8, planHash: role }));
      return;
    }
    if (request.url === '/v1/database/inspect') {
      response.end(JSON.stringify({ source: 'PROCEDURE GET_STATUS IS BEGIN NULL; EXCEPTION WHEN OTHERS THEN RAISE; END;' }));
      return;
    }
    response.statusCode = 404;
    response.end(JSON.stringify({ error: { code: 'NOT_FOUND' } }));
  });
}

function option(name, fallback) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : fallback;
}

if (import.meta.url === `file:///${process.argv[1]?.replaceAll('\\', '/')}`) {
  const role = option('--role', 'baseline');
  const port = Number(option('--port', '4101'));
  createMockApi(role).listen(port, () => console.log(`Mock ${role}: http://127.0.0.1:${port}`));
}
