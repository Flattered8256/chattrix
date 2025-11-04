// API错误响应类型
export interface APIErrorResponse {
  code: number;
  message: string;
  data: any;
}

// 自定义API错误类
export class APIError extends Error {
  public status: number;
  public data: any;
  
  constructor(status: number, data: any, message: string) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

// 类型守卫函数，检查是否为AxiosError
function isAxiosError(error: unknown): error is import('axios').AxiosError {
  return error instanceof Error && 'isAxiosError' in error && (error as any).isAxiosError === true;
}

// 统一错误处理函数
export function handleApiError(error: unknown): never {
  if (isAxiosError(error)) {
    const apiError = new APIError(
      error.response?.status || 500,
      error.response?.data || null,
      (error.response?.data as { message?: string })?.message || error.message
    );
    throw apiError;
  } else if (error instanceof Error) {
    // 对于其他类型的错误，保留原始错误消息
    throw error;
  } else {
    // 只有在无法获取任何具体信息时才使用通用错误消息
    throw new Error('An unexpected error occurred');
  }
}
