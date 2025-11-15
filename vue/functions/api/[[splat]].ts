export async function onRequest({ request, params }) {
  const url = new URL(request.url)
  
  // 从原始 URL 中提取路径，避免 params.splat 的问题
  const originalPath = url.pathname.replace(/^\/api\//, '')
  
  const target = `https://practical-becky-chattrix-f0677ddd.koyeb.app/api/${originalPath}`
   
  return fetch(target, {
    method: request.method,
    headers: request.headers,
    body: request.body
  })
}