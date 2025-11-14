<template>
  <div class="register-form">
    <h2 class="form-title">用户注册</h2>
    <el-form
      ref="registerFormRef"
      :model="form"
      :rules="rules"
      @submit.prevent="handleRegister"
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

      <el-form-item label="确认密码" prop="password_confirm">
        <el-input
          v-model="form.password_confirm"
          type="password"
          placeholder="请再次输入密码"
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
          {{ isLoading ? "注册中..." : "注册" }}
        </el-button>
      </el-form-item>
    </el-form>

    <div class="form-footer">
      <p class="redirect-text">
        已有账号？
        <router-link to="/login" class="redirect-link">立即登录</router-link>
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
import type { RegisterRequest } from "../../api/auth";

// 表单引用
const registerFormRef = ref<FormInstance>();

// 表单数据
const form = reactive<RegisterRequest>({
  username: "",
  password: "",
  password_confirm: "",
});

// 自定义验证器：确认密码
const validatePasswordConfirm = (rule: any, value: string, callback: any) => {
  if (value === "") {
    callback(new Error("请再次输入密码"));
  } else if (value !== form.password) {
    callback(new Error("两次输入的密码不一致"));
  } else {
    callback();
  }
};

// 表单验证规则
const rules = reactive<FormRules<RegisterRequest>>({
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    {
      min: 3,
      max: 20,
      message: "用户名长度在 3 到 20 个字符",
      trigger: "blur",
    },
    {
      pattern: /^[a-zA-Z0-9_]+$/,
      message: "用户名只能包含字母、数字和下划线",
      trigger: "blur",
    },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码长度至少 6 个字符", trigger: "blur" },
  ],
  password_confirm: [
    { required: true, validator: validatePasswordConfirm, trigger: "blur" },
  ],
});

// 状态管理
const authStore = useAuthStore();
const router = useRouter();

// 组件状态
const isLoading = ref(false);

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return;

  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return;

    isLoading.value = true;

    try {
      const result = await authStore.register(form);

      if (result.success) {
        ElMessage.success("注册成功，请登录");
        router.push("/login");
      } else {
        ElMessage.error(result.error || "注册失败");
      }
    } catch (error) {
      ElMessage.error("注册过程中发生错误");
      console.error("Register error:", error);
    } finally {
      isLoading.value = false;
    }
  });
};
</script>

<style scoped>
.register-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 2.5rem;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.form-title {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.75rem;
  font-weight: 600;
}

.form-footer {
  margin-top: 1.5rem;
  text-align: center;
}

.redirect-text {
  color: #606266;
  font-size: 0.9rem;
}

.redirect-link {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}

.redirect-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}
</style>
