import { get, post, patch, type ApiResponse } from './https';
import { handleApiError, APIError } from './error';

// 定义用户类型
export interface User {
  id: number;
  username: string;
  user_avatar?: string;
  user_status?: string;
}

// 登录请求参数类型
export interface LoginRequest {
  username: string;
  password: string;
}

// 注册请求参数类型
export interface RegisterRequest {
  username: string;
  password: string;
  password_confirm: string;
}

// 用户资料更新参数类型
export interface UserUpdateRequest {
  user_avatar?: File;
  username?: string;
}

// 登录响应数据类型
export interface LoginResponseData {
  user: User;
  refresh: string;
  access: string;
}

// 搜索用户参数类型
export interface SearchUserRequest {
  id: number;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
  confirm_password: string;
}


// 用户登录
export async function login(request: LoginRequest): Promise<ApiResponse<LoginResponseData>> {
  try {
    return await post('api/accounts/login/', request);
  } catch (error) {
    throw handleApiError(error); // 修改为 throw 而不是 return
  }
}

// 用户注册
export async function register(request: RegisterRequest): Promise<ApiResponse<User>> {
  try {
    return await post('api/accounts/register/', request);
  } catch (error) {
    throw handleApiError(error); // 修改为 throw 而不是 return
  }
}

// 刷新令牌
export async function refreshToken(): Promise<ApiResponse<{ refresh: string; access: string }>> {
  try {
    return await post('api/accounts/refresh/');
  } catch (error) {
    throw handleApiError(error); // 修改为 throw 而不是 return
  }
}

// 用户登出
export async function logout(refreshToken: string): Promise<ApiResponse<null>> {
  try {
    return await post('api/accounts/logout/', { refresh: refreshToken });
  } catch (error) {
    throw handleApiError(error);
  }
}

// 搜索用户
export async function searchUser(params: SearchUserRequest): Promise<ApiResponse<User>> {
  // 验证ID是否为10位数字
  if (!params.id || params.id.toString().length !== 10) {
    return Promise.reject(
      new APIError(400, { id: ['UID must be a 10-digit number.'] }, 'Validation error')
    );
  }
  
  try {
    return await get('api/accounts/search/', { params });
  } catch (error) {
    throw handleApiError(error);
  }
}

// 获取当前用户资料
export async function getCurrentUser(): Promise<ApiResponse<User>> {
  try {
    return await get('api/accounts/getprofile/');
  } catch (error) {
    throw handleApiError(error);
  }
}

// 更新用户资料
export async function updateProfile(request: UserUpdateRequest): Promise<ApiResponse<User>> {
  try {
    return await patch('api/accounts/profile/', request);
  } catch (error) {
    throw handleApiError(error);
  }
}



// 上传用户头像
export async function uploadAvatar(avatarFile: File): Promise<ApiResponse<User>> {
  try {
    // 创建 FormData 对象用于文件上传
    const formData = new FormData();
    formData.append('user_avatar', avatarFile);
    
    // 使用 multipart/form-data 格式发送请求
    return await patch('api/accounts/profile/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  } catch (error) {
    throw handleApiError(error);
  }
}

// 更新用户资料（支持头像上传）

export async function updateProfileWithAvatar(request: UserUpdateRequest): Promise<ApiResponse<User>> {
  try {
    if (request.user_avatar instanceof File) {
      // 明确使用 FormData 处理文件上传
      const formData = new FormData();
      Object.entries(request).forEach(([key, value]) => {
        formData.append(key, value);
      });

      return await patch('api/accounts/profile/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
    } else {
      // 否则发送普通 JSON 数据
      return await patch('api/accounts/profile/', request);
    }
  } catch (error) {
    throw handleApiError(error);
  }
}

export async function changePassword(request: ChangePasswordRequest): Promise<ApiResponse<null>> {
  try {
    return await post('api/accounts/change-password/', request);
  } catch (error) {
    throw handleApiError(error);
  }
}