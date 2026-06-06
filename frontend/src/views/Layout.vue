<template>
  <el-container style="height:100vh">
    <el-aside width="220px" style="background:#1f2d3d">
      <div class="logo">K8s Manager</div>
      <el-menu
        :default-active="route.path"
        router
        background-color="#1f2d3d"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/clusters">
          <el-icon><Connection /></el-icon>
          <span>集群管理</span>
        </el-menu-item>
        <el-menu-item index="/workloads">
          <el-icon><Grid /></el-icon>
          <span>工作负载</span>
        </el-menu-item>
        <el-menu-item index="/services">
          <el-icon><Share /></el-icon>
          <span>服务网络</span>
        </el-menu-item>
        <el-menu-item index="/nodes">
          <el-icon><Monitor /></el-icon>
          <span>节点管理</span>
        </el-menu-item>
        <el-menu-item index="/audit">
          <el-icon><Document /></el-icon>
          <span>审计日志</span>
        </el-menu-item>
        <el-menu-item v-if="store.isAdmin" index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display:flex;justify-content:flex-end;align-items:center;border-bottom:1px solid #dcdfe6">
        <span style="margin-right:16px">{{ store.username }}</span>
        <el-button text @click="handleLogout">退出</el-button>
      </el-header>
      <el-main style="background:#f5f7fa">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
const route = useRoute()
const router = useRouter()
const store = useAppStore()

function handleLogout() {
  store.logout()
  router.push('/login')
}
</script>

<style scoped>
.logo { color:#fff; font-size:18px; text-align:center; padding:20px 0; font-weight:bold; }
</style>
