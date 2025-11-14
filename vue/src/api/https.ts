import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios';
import { APIError } from './error'; // 从error.ts导入

// API 基础配置
const API_BASE_URL = '';
const REQUEST_TIMEOUT = 10000; // 10秒超时

// 存储相关的工具函数
const TOKEN_KEY = 'accessToken';
const REFRESH_TOKEN_KEY = 'refreshToken';

/**
 * 获取存储的 token
 */
export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * 获取存储的 refresh token
 */
export function getStoredRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * 存储 token
 */
export function storeToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * 存储 refresh token
 */
export function storeRefreshToken(token: string): void {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

/**
 * 清除存储的 token
 */
export function clearStoredTokens(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * API 响应数据的标准格式
 */
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

/**
 * 创建 axios 实例
 */
const httpClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 请求拦截器
 * 在发送请求前添加认证 token
 */
httpClient.interceptors.request.use(
  (config: import('axios').InternalAxiosRequestConfig) => {
    const token = getStoredToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

/**
 * 响应拦截器
 * 处理 token 过期和统一错误处理
 */
httpClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError<ApiResponse>) => {
    const originalRequest = error.config;

    // 处理 401 未授权错误
    if (error.response?.status === 401 && originalRequest && !(originalRequest as any)._retry) {
      (originalRequest as any)._retry = true;

      try {
        const refreshToken = getStoredRefreshToken();
        if (refreshToken) {
          // 尝试刷新 token
          const response = await axios.post(`${API_BASE_URL}api/accounts/refresh/`, {
            refresh: refreshToken,
          });

          const { access, refresh } = response.data.data;
          storeToken(access);
          storeRefreshToken(refresh);

          // 重试原请求
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access}`;
          }
          return httpClient(originalRequest);
        }
      } catch (refreshError) {
        // 刷新失败，清除 token 并跳转到登录页
        clearStoredTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // 统一错误处理
    if (error.response) {
      const apiError = new APIError(
        error.response.status,
        error.response.data,
        error.response.data?.message || error.message
      );
      return Promise.reject(apiError);
    }

    return Promise.reject(error);
  }
);

/**
 * GET 请求封装
 */
export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  const response = await httpClient.get<ApiResponse<T>>(url, config);
  return response.data;
}

/**
 * POST 请求封装
 */
export async function post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  const response = await httpClient.post<ApiResponse<T>>(url, data, config);
  return response.data;
}

/**
 * PUT 请求封装
 */
export async function put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  const response = await httpClient.put<ApiResponse<T>>(url, data, config);
  return response.data;
}

/**
 * PATCH 请求封装
 */
export async function patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  const response = await httpClient.patch<ApiResponse<T>>(url, data, config);
  return response.data;
}

/**
 * DELETE 请求封装
 */
export async function remove<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  const response = await httpClient.delete<ApiResponse<T>>(url, config);
  return response.data;
}

/**
 * 上传文件封装
 */
export async function uploadFile<T>(
  url: string, 
  formData: FormData, 
  timeout: number = 1000 * 60 * 5 // 默认 5 分钟超时
): Promise<ApiResponse<T>> {
  // 分块上传实现说明：
  // - 如果 formData 中包含名为 'file' 的 File 且文件大小大于 chunkSize，则按块上传。
  // - 每个块构建一个新的 FormData，包含: file(该块)、uploadId、chunkIndex、totalChunks、filename（后端可据此重组）。
  // - 上传按序进行（可扩展为并发），每块最多重试 3 次。
  // - onUploadProgress 回调用于报告单个块的上传进度，结合全局进度计算整个文件进度。

  // 辅助函数
  function generateUploadId() {
    return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
  }

  function sleep(ms: number) {
    return new Promise((res) => setTimeout(res, ms));
  }

  // 从 FormData 中尝试获取 File 对象
  function getFileFromFormData(fd: FormData): File | null {
    try {
      const maybeFile = fd.get('file');
      if (maybeFile instanceof File) return maybeFile;
      return null;
    } catch (e) {
      return null;
    }
  }

  // 默认分块大小 5MB
  const DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024;
  const file = getFileFromFormData(formData);

  // 如果没有文件或文件较小，则使用原有一次性上传逻辑
  if (!file || file.size <= DEFAULT_CHUNK_SIZE) {
    const response = await httpClient.post<ApiResponse<T>>(url, formData, {
      timeout,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // 分块上传逻辑
  const chunkSize = DEFAULT_CHUNK_SIZE;
  const totalChunks = Math.ceil(file.size / chunkSize);
  const uploadId = generateUploadId();

  // 允许外部通过 formData 设置回调（非标准），例如 formData.append('__onProgress', '...')
  // 这里我们不读取该字段；建议调用方传入回调参数（见下面导出函数）。

  // 逐块上传。返回最后一次成功响应（通常后端在最后一个块时返回合并结果）
  let lastResponse: import('axios').AxiosResponse<any> | null = null;

  for (let index = 0; index < totalChunks; index++) {
    const start = index * chunkSize;
    const end = Math.min(start + chunkSize, file.size);
    const chunkBlob = file.slice(start, end);

    const chunkForm = new FormData();
    // 把除了 file 之外的其它字段从原 formData 复制到 chunkForm
    for (const [k, v] of (formData as any).entries()) {
      if (k === 'file') continue;
      chunkForm.append(k, v as any);
    }

    // 文件字段：后端应把这些字段用于拼接
    chunkForm.append('file', chunkBlob, file.name);
    chunkForm.append('uploadId', uploadId);
    chunkForm.append('chunkIndex', String(index));
    chunkForm.append('totalChunks', String(totalChunks));
    chunkForm.append('filename', file.name);

    // 每块最多重试次数
    const maxRetries = 3;
    let attempt = 0;
    let success = false;
    let lastErr: any = null;

    while (attempt < maxRetries && !success) {
      try {
        lastResponse = await httpClient.post<ApiResponse<T>>(url, chunkForm, {
          timeout,
          headers: {
            'Content-Type': 'multipart/form-data',
            // 也可以选择在 header 中传递 chunk 信息：
            'X-Upload-Id': uploadId,
            'X-Chunk-Index': String(index),
            'X-Total-Chunks': String(totalChunks),
          },
          onUploadProgress: (_progressEvent: import('axios').AxiosProgressEvent) => {
            // 触发单块上传进度（浏览器层面），可用于合成全局进度
            // 这里不直接做任何 UI 回调；调用方应传入自己的回调以便监听进度。
            // 如果需要暴露进度，可扩展 uploadFile 接口以接收 onProgress 参数。
          },
        });

        success = true;
      } catch (err) {
        lastErr = err;
        attempt += 1;
        // 简单的指数回退
        await sleep(500 * attempt);
      }
    }

    if (!success) {
      // 如果某块最终上传失败，抛出错误（外层调用可捕获并处理）
      throw lastErr || new Error('Chunk upload failed');
    }
  }

  // 至少有一次成功响应
  if (!lastResponse) {
    throw new Error('上传失败：没有服务器响应');
  }

  return lastResponse.data;
}


/**
 * 下载文件封装
 */
export async function downloadFile(url: string, filename?: string): Promise<void> {
  const response = await httpClient.get(url, {
    responseType: 'blob',
  });

  // 创建下载链接
  const blob = new Blob([response.data]);
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = filename || 'download';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);
}

/**
 * 取消请求的工具
 */
export function createCancelToken() {
  return axios.CancelToken.source();
}

/**
 * 检查网络连接
 */
export function isOnline(): boolean {
  return navigator.onLine;
}

/**
 * 获取错误消息
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof APIError) {
    return error.message;
  } else if (axios.isAxiosError(error)) {
    return error.response?.data?.message || error.message;
  } else if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
}

// 导出 axios 实例以供直接使用
export { httpClient };
export default httpClient;