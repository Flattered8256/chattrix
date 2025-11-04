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
export async function uploadFile<T>(url: string, file: File, fieldName: string = 'file'): Promise<ApiResponse<T>> {
  const formData = new FormData();
  formData.append(fieldName, file);

  const response = await httpClient.post<ApiResponse<T>>(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
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