export async function onRequest({ request, params }) {
  const url = new URL(request.url)
  
  // 从原始 URL 中提取路径，避免 params.splat 的问题
  const originalPath = url.pathname.replace(/^\/api\//, '')

  // 包含查询字符串（url.search），避免丢失 ?id=... 等参数
  const target = `https://practical-becky-chattrix-f0677ddd.koyeb.app/api/${originalPath}${url.search}`

  // 使用新的 Request 将原始请求的 method/headers/body 复制到目标 URL
  const forwarded = new Request(target, request)
  return fetch(forwarded)
}