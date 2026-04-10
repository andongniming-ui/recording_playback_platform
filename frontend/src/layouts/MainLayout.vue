<template>
  <n-layout has-sider style="height: 100vh">
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="220"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <div class="logo">
        <span v-if="!collapsed">AREX 录制平台</span>
        <span v-else>AREX</span>
      </div>
      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleMenuSelect"
      />
    </n-layout-sider>
    <n-layout>
      <n-layout-header class="header" bordered>
        <span class="title">{{ currentTitle }}</span>
        <n-space>
          <n-text>{{ userStore.username }}</n-text>
          <n-button text @click="logout">退出登录</n-button>
        </n-space>
      </n-layout-header>
      <n-layout-content style="padding: 24px; overflow: auto">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NLayout, NLayoutContent, NLayoutHeader, NLayoutSider, NMenu, NSpace, NText } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const collapsed = ref(false)

const menuOptions: MenuOption[] = [
  { label: '仪表盘', key: 'dashboard' },
  { label: '应用管理', key: 'applications' },
  { label: '录制中心', key: 'recording' },
  { label: '测试用例', key: 'testcases' },
  { label: '回放执行', key: 'replay' },
  { label: '对比规则', key: 'compare' },
  { label: '执行结果', key: 'results' },
  { label: '定时任务', key: 'schedule' },
  { label: '测试套件', key: 'suites' },
  { label: 'CI 集成', key: 'ci' },
  { label: '用户管理', key: 'users' },
  { label: '系统设置', key: 'settings' },
]

const titleMap: Record<string, string> = {
  dashboard: '仪表盘',
  applications: '应用管理',
  recording: '录制中心',
  testcases: '测试用例',
  replay: '回放执行',
  compare: '对比规则',
  results: '执行结果',
  schedule: '定时任务',
  suites: '测试套件',
  ci: 'CI 集成',
  users: '用户管理',
  settings: '系统设置',
}

const activeKey = computed(() => route.path.split('/')[1] || 'dashboard')
const currentTitle = computed(() => titleMap[activeKey.value] || 'AREX 录制平台')

function handleMenuSelect(key: string) {
  router.push(`/${key}`)
}

function logout() {
  userStore.clearUser()
  router.push('/login')
}
</script>

<style scoped>
.logo {
  padding: 16px;
  font-size: 16px;
  font-weight: 700;
  color: #18a058;
}

.header {
  height: 56px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title {
  font-size: 16px;
  font-weight: 600;
}
</style>
