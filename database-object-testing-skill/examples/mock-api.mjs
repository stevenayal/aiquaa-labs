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
      if (typeof body.arguments?.displayName === 'string') {
        const value = body.arguments.displayName;
        if ([...value].length > 100) {
          response.statusCode = 422;
          response.end(JSON.stringify({ error: { code: 'VALUE_TOO_LONG', message: 'DISPLAY_NAME supera 100 caracteres' } }));
          return;
        }
        const truncates = role === 'impact-truncating' && body.object?.name === 'SP_SYNC_CUSTOMER';
        const persistedValue = truncates && [...value].length > 50 ? [...value].slice(0, 50).join('') : value;
        response.end(JSON.stringify({ data: { persistedValue, operation: body.arguments.mode } }));
        return;
      }
      response.end(JSON.stringify({
        data: { rows: [{ customerId: body.arguments?.customerId, status: 'ACTIVE' }], rowCount: 1, out: { status: 'ACTIVE' } },
        metrics: { elapsedMs: role === 'candidate' ? 11 : 10 }
      }));
      return;
    }
    if (request.url === '/v1/database/dependencies') {
      const syncLength = role === 'impact-truncating' ? 50 : 100;
      response.end(JSON.stringify({
        discoveredAt: new Date().toISOString(),
        dependencies: [
          {
            id: 'CRM.PKG_CUSTOMER.UPSERT_CUSTOMER',
            object: { schema: 'CRM', name: 'PKG_CUSTOMER.UPSERT_CUSTOMER', type: 'package' },
            operations: ['INSERT', 'UPDATE'],
            invocations: [
              {
                id: 'insert-customer', operation: 'INSERT', effectiveLength: 100, transformations: [],
                request: { object: { schema: 'CRM', name: 'PKG_CUSTOMER.UPSERT_CUSTOMER' }, operation: 'execute', arguments: { customerId: 900001, mode: 'INSERT', displayName: '' } },
                valuePath: '$.arguments.displayName', resultPath: '$.data.persistedValue'
              },
              {
                id: 'update-customer', operation: 'UPDATE', effectiveLength: 100, transformations: [],
                request: { object: { schema: 'CRM', name: 'PKG_CUSTOMER.UPSERT_CUSTOMER' }, operation: 'execute', arguments: { customerId: 900002, mode: 'UPDATE', displayName: '' } },
                valuePath: '$.arguments.displayName', resultPath: '$.data.persistedValue'
              }
            ]
          },
          {
            id: 'CRM.SP_SYNC_CUSTOMER',
            object: { schema: 'CRM', name: 'SP_SYNC_CUSTOMER', type: 'procedure' },
            operations: ['UPDATE'],
            invocations: [
              {
                id: 'sync-update', operation: 'UPDATE', effectiveLength: syncLength,
                transformations: role === 'impact-truncating' ? ['SUBSTR(display_name, 1, 50)'] : [],
                request: { object: { schema: 'CRM', name: 'SP_SYNC_CUSTOMER' }, operation: 'execute', arguments: { customerId: 900003, mode: 'UPDATE', displayName: '' } },
                valuePath: '$.arguments.displayName', resultPath: '$.data.persistedValue'
              }
            ]
          }
        ],
        unresolved: role === 'impact-unresolved'
          ? [{ id: 'CRM.PKG_DYNAMIC', objectType: 'package', reason: 'SQL dinámico construido en runtime' }]
          : []
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
