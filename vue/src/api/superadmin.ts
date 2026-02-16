import { get, post, put, patch, remove, type ApiResponse } from './https';
import { handleApiError } from './error';
import { type LoginRequest, type LoginResponseData } from './auth';

// 重新导出登录相关类型
export type { LoginRequest, LoginResponseData };

// 用户类型定义
export interface User {
  id: number;
  username: string;
  user_avatar: string | null;
  date_joined: string;
}

// 用户更新类型定义
export interface UserUpdate {
  username?: string;
  user_avatar?: string | null;
}

// 用户登录
export async function login(request: LoginRequest): Promise<ApiResponse<LoginResponseData>> {
  try {
    return await post('api/superadmin/login/', request);
  } catch (error) {
    throw handleApiError(error); // 修改为 throw 而不是 return
  }
}

/**
 * 获取用户列表
 * @returns 用户列表数据
 */
export async function getUserList(): Promise<ApiResponse<User[]>> {
  try {
    return await get('api/superadmin/users/');
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * 更新用户信息
 * @param userId 用户ID
 * @param data 更新数据
 * @returns 更新后的用户信息
 */
export async function updateUser(userId: number, data: UserUpdate): Promise<ApiResponse<User>> {
  try {
    return await put(`api/superadmin/users/${userId}/`, data);
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * 部分更新用户信息
 * @param userId 用户ID
 * @param data 更新数据
 * @returns 更新后的用户信息
 */
export async function patchUser(userId: number, data: Partial<UserUpdate>): Promise<ApiResponse<User>> {
  try {
    return await patch(`api/superadmin/users/${userId}/`, data);
  } catch (error) {
    throw handleApiError(error);
  }
}

/**
 * 删除用户
 * @param userId 用户ID
 * @returns 操作结果
 */
export async function deleteUser(userId: number): Promise<ApiResponse<null>> {
  try {
    return await remove(`api/superadmin/users/${userId}/`);
  } catch (error) {
    throw handleApiError(error);
  }
}