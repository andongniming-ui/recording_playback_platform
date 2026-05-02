<template>
  <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:60vh;gap:16px">
    <n-result status="404" title="页面不存在" description="你访问的页面不存在或已被删除">
      <template #footer>
        <n-space justify="center">
          <n-button type="primary" @click="router.push('/dashboard')">返回首页</n-button>
          <n-button @click="router.back()">返回上一页</n-button>
        </n-space>
      </template>
    </n-result>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { NResult, NButton, NSpace } from 'naive-ui'

const router = useRouter()
</script>
