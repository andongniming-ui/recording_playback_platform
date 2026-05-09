<template>
  <div style="display: flex; justify-content: center; align-items: center; height: 100vh; background: #f5f5f5">
    <n-card title="Recorder 登录" style="width: 400px">
      <n-form ref="formRef" :model="form" :rules="rules">
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="form.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="密码" path="password">
          <n-input v-model:value="form.password" type="password" placeholder="请输入密码" @keyup.enter="handleLogin" />
        </n-form-item>
        <n-button type="primary" block :loading="loading" @click="handleLogin">登录</n-button>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton, useMessage } from 'naive-ui'
import api from '@/api'
import { useUserStore } from '@/store/user'
import { extractError } from '@/utils/error'

const router = useRouter()
const route = useRoute()
const message = useMessage()
const userStore = useUserStore()
const loading = ref(false)
const formRef = ref()

const form = ref({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名' }],
  password: [{ required: true, message: '请输入密码' }],
}

async function handleLogin() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('username', form.value.username)
    params.append('password', form.value.password)
    const resp = await api.post('/auth/login', params)
    userStore.setUser({
      access_token: resp.data.access_token,
      username: resp.data.username || form.value.username,
      role: resp.data.role || 'viewer',
    })
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
    router.push(redirect)
  } catch (e: unknown) {
    message.error(extractError(e, 'Login failed'))
  } finally {
    loading.value = false
  }
}
</script>
