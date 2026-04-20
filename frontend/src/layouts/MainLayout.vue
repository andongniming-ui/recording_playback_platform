<template>
  <n-layout class="app-shell" has-sider>
    <div class="shell-bg shell-bg--left"></div>
    <div class="shell-bg shell-bg--right"></div>

    <n-layout-sider
      class="app-sider"
      collapse-mode="width"
      :collapsed-width="72"
      :width="252"
      :collapsed="collapsed"
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <div class="brand" @click="collapsed = !collapsed">
        <div class="brand-mark">AR</div>
        <div v-if="!collapsed" class="brand-copy">
          <div class="brand-title">AREX Recorder</div>
          <div class="brand-subtitle">录制、回放、对比</div>
        </div>
      </div>

      <div v-if="!collapsed" class="brand-panel">
        <div class="brand-panel__label">当前页面</div>
        <div class="brand-panel__value">{{ pageTitle }}</div>
        <div class="brand-panel__meta">{{ todayLabel }}</div>
      </div>

      <n-menu
        class="side-menu"
        :collapsed="collapsed"
        :collapsed-width="72"
        :collapsed-icon-size="20"
        :options="visibleMenuOptions"
        :value="activeKey"
        @update:value="handleNav"
      />
    </n-layout-sider>

    <n-layout class="app-main">
      <div class="topbar">
        <div>
          <div class="topbar-title-row">
            <div class="topbar-title">{{ pageTitle }}</div>
          </div>
          <div class="topbar-subtitle">面向录制同步、回放验证和双环境差异检查的统一平台</div>
        </div>
        <n-space align="center" size="small">
          <div class="topbar-date">{{ todayLabel }}</div>
          <n-button v-if="route.path !== '/dashboard'" quaternary size="small" @click="router.push('/dashboard')">总览</n-button>
        </n-space>
      </div>

      <n-layout-content class="app-content" content-style="padding: 0 24px 24px;">
        <div class="content-shell">
          <router-view />
        </div>
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { computed, h, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NLayout, NLayoutContent, NLayoutSider, NMenu, NSpace } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import { useUserStore } from '@/store/user'

const collapsed = ref(false)
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeKey = computed(() => {
  const p = route.path
  if (p.startsWith('/dashboard')) return 'dashboard'
  if (p.startsWith('/applications')) return 'applications'
  if (p.startsWith('/recording')) return 'recording'
  if (p.startsWith('/testcases')) return 'testcases'
  if (p === '/replay') return 'replay'
  if (p.startsWith('/replay/history') || p.startsWith('/results')) return 'replay-history'
  if (p.startsWith('/suites')) return 'suites'
  if (p.startsWith('/schedule')) return 'schedule'
  if (p.startsWith('/compare')) return 'compare'
  if (p.startsWith('/ci')) return 'ci'
  if (p.startsWith('/settings')) return 'settings'
  if (p.startsWith('/users')) return 'users'
  return 'applications'
})

const pageTitleMap: Record<string, string> = {
  dashboard: '数据总览',
  applications: '应用管理',
  recording: '录制中心',
  testcases: '测试用例库',
  replay: '发起回放',
  'replay-history': '回放历史',
  suites: '回放套件',
  schedule: '定时回放',
  compare: '双环境对比',
  ci: 'CI 集成',
  settings: '平台指引',
  users: '用户管理',
}

const pageTitle = computed(() => pageTitleMap[activeKey.value] || 'AREX Recorder')

const todayLabel = computed(() => {
  const now = new Date()
  const week = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const mm = String(now.getMonth() + 1).padStart(2, '0')
  const dd = String(now.getDate()).padStart(2, '0')
  return `${mm}/${dd} ${week[now.getDay()]}`
})

const menuOptions: MenuOption[] = [
  { label: '数据总览', key: 'dashboard', icon: () => h('span', '概') },
  { label: '应用管理', key: 'applications', icon: () => h('span', '应') },
  { label: '录制中心', key: 'recording', icon: () => h('span', '录') },
  { label: '测试用例库', key: 'testcases', icon: () => h('span', '例') },
  { label: '发起回放', key: 'replay', icon: () => h('span', '回') },
  { label: '回放历史', key: 'replay-history', icon: () => h('span', '史') },
  { label: '回放套件', key: 'suites', icon: () => h('span', '套') },
  { label: '定时回放', key: 'schedule', icon: () => h('span', '定') },
  { label: '双环境对比', key: 'compare', icon: () => h('span', '比') },
  { label: 'CI 集成', key: 'ci', icon: () => h('span', 'CI') },
  { label: '用户管理', key: 'users', icon: () => h('span', '用') },
  { label: '平台指引', key: 'settings', icon: () => h('span', '指') },
]

const visibleMenuOptions = computed(() =>
  menuOptions.filter((item) => {
    if (item.key === 'compare' || item.key === 'ci' || item.key === 'users' || item.key === 'settings') {
      return false
    }
    return !(item.key === 'users' || item.key === 'ci') || userStore.role === 'admin'
  }),
)

function handleNav(key: string) {
  if (key === 'replay-history') {
    router.push('/replay/history')
    return
  }
  router.push(`/${key}`)
}
</script>

<style scoped>
.app-shell {
  position: relative;
  height: 100vh;
  min-height: 100vh;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(24, 160, 88, 0.12), transparent 28%),
    radial-gradient(circle at bottom right, rgba(24, 115, 232, 0.10), transparent 30%),
    linear-gradient(180deg, #f7f9fc 0%, #edf3f8 100%);
}

.shell-bg {
  position: fixed;
  pointer-events: none;
  border-radius: 999px;
  filter: blur(12px);
  opacity: 0.6;
}

.shell-bg--left {
  top: -64px;
  left: -80px;
  width: 260px;
  height: 260px;
  background: rgba(24, 160, 88, 0.12);
}

.shell-bg--right {
  right: 40px;
  top: 120px;
  width: 220px;
  height: 220px;
  background: rgba(24, 115, 232, 0.10);
}

.app-sider {
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: relative;
  z-index: 1;
  background: linear-gradient(180deg, #17324d 0%, #0f2437 100%);
  box-shadow: 18px 0 40px rgba(15, 36, 55, 0.12);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 92px;
  padding: 22px 20px 18px;
  cursor: pointer;
}

.brand-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f08a5d 0%, #f6bd60 100%);
  color: #0f2437;
  font-size: 14px;
  font-weight: 800;
}

.brand-copy {
  min-width: 0;
}

.brand-title {
  color: #f8fbff;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.brand-subtitle {
  margin-top: 3px;
  color: rgba(226, 236, 247, 0.72);
  font-size: 13px;
}

.brand-panel {
  margin: 4px 16px 16px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.06);
}

.brand-panel__label {
  color: rgba(226, 236, 247, 0.66);
  font-size: 11px;
  letter-spacing: 0.08em;
}

.brand-panel__value {
  margin-top: 8px;
  color: #fff7ef;
  font-size: 19px;
  font-weight: 700;
}

.brand-panel__meta {
  margin-top: 8px;
  color: rgba(226, 236, 247, 0.72);
  font-size: 13px;
}

.side-menu {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 10px 12px 22px;
}

.app-main {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  position: relative;
  z-index: 1;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  min-height: 86px;
  padding: 16px 28px;
  border-bottom: 1px solid rgba(15, 36, 55, 0.08);
  background: rgba(247, 249, 252, 0.88);
  backdrop-filter: blur(18px);
}

.topbar-title-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.topbar-title {
  color: #102132;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: 0.01em;
}

.topbar-subtitle {
  margin-top: 6px;
  color: #627085;
  font-size: 13px;
}

.topbar-date {
  color: #7d8a99;
  font-size: 13px;
}

.app-content {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding-top: 20px;
}

.content-shell {
  min-height: calc(100vh - 122px);
  padding: 20px 20px 24px;
  border: 1px solid rgba(15, 36, 55, 0.06);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.06);
}

:deep(.n-menu) {
  background: transparent;
}

:deep(.n-menu .n-menu-item-content) {
  height: 50px;
  border-radius: 14px;
  margin-bottom: 10px;
}

:deep(.n-menu .n-menu-item-content .n-menu-item-content-header),
:deep(.n-menu .n-submenu-item-content-header) {
  color: rgba(255, 255, 255, 0.86);
  font-size: 15px;
  font-weight: 600;
}

:deep(.n-menu .n-menu-item-content:hover .n-menu-item-content-header),
:deep(.n-menu .n-submenu-item-content:hover .n-submenu-item-content-header) {
  color: #ffffff;
}

:deep(.n-menu .n-menu-item-content--selected),
:deep(.n-menu .n-menu-item-content--child-active) {
  background: linear-gradient(135deg, rgba(240, 138, 93, 0.22), rgba(246, 189, 96, 0.14));
}

:deep(.n-menu .n-menu-item-content--selected .n-menu-item-content-header),
:deep(.n-menu .n-menu-item-content--child-active .n-menu-item-content-header),
:deep(.n-menu .n-menu-item-content--selected .n-submenu-item-content-header),
:deep(.n-menu .n-menu-item-content--child-active .n-submenu-item-content-header) {
  color: #ffffff;
}

:deep(.n-menu .n-menu-item-content__icon) {
  width: 24px;
  height: 24px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.86);
}

:deep(.n-menu .n-menu-item-content--selected .n-menu-item-content__icon),
:deep(.n-menu .n-menu-item-content--child-active .n-menu-item-content__icon) {
  background: rgba(255, 255, 255, 0.18);
  color: #ffffff;
}

:deep(.n-layout-content) {
  color: #1f2a37;
}
</style>
