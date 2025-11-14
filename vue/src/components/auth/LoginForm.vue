<template>
  <div class="login-form">
    <h2 class="form-title">用户登录</h2>
    <el-form
      ref="loginFormRef"
      :model="form"
      :rules="rules"
      @submit.prevent="handleLogin"
      label-position="top"
      size="large"
    >
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" clearable>
          <template #prefix>
            <el-icon><User /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          show-password
          clearable
        >
          <template #prefix>
            <el-icon><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          native-type="submit"
          :loading="isLoading"
          style="width: 100%"
        >
          {{ isLoading ? "登录中..." : "登录" }}
        </el-button>
      </el-form-item>
    </el-form>

    <div class="form-footer">
      <p class="redirect-text">
        还没有账号？
        <router-link to="/register" class="redirect-link">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { User, Lock } from "@element-plus/icons-vue";
import { useAuthStore } from "../../store/auth";
import type { LoginRequest } from "../../api/auth";

// 表单引用
const loginFormRef = ref<FormInstance>();

// 表单数据
const form = reactive<LoginRequest>({
  username: "",
  password: "",
});

// 表单验证规则
const rules = reactive<FormRules<LoginRequest>>({
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    {
      min: 3,
      max: 20,
      message: "用户名长度在 3 到 20 个字符",
      trigger: "blur",
    },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码长度至少 6 个字符", trigger: "blur" },
  ],
});

// 状态管理
const authStore = useAuthStore();
const router = useRouter();

// 组件状态
const isLoading = ref(false);

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return;

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return;

    isLoading.value = true;

    try {
      const result = await authStore.login(form);

      if (result.success) {
        ElMessage.success("登录成功");
        setTimeout(() => {
          router.push("/chat");
        }, 1000);
      } else {
        ElMessage.error(result.error || "登录失败");
      }
    } finally {
      isLoading.value = false;
    }
  });
};
</script>

<style lang="scss" scoped>
// 登录表单容器
.login-form {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 2.5rem;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

// 表单标题
.form-title {
  text-align: center;
  margin-bottom: 2rem;
  color: #303133;
  font-size: 1.75rem;
  font-weight: 600;
}

// 表单底部
.form-footer {
  margin-top: 1.5rem;
  text-align: center;

  // 嵌套：重定向文本
  .redirect-text {
    color: #606266;
    font-size: 0.9rem;
  }

  // 嵌套：重定向链接
  .redirect-link {
    color: #409eff;
    text-decoration: none;
    font-weight: 500;

    // 使用 & 选择器继承
    &:hover {
      color: #66b1ff;
      text-decoration: underline;
    }

    &:active {
      color: #3a8ee6;
    }

    &:focus {
      outline: 2px solid #409eff;
      outline-offset: 2px;
    }
  }
}
</style>
