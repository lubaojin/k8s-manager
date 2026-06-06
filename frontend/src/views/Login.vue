<template>
  <div class="login-wrapper">
    <el-card class="login-card">
      <h2>K8s Manager</h2>
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" style="width:100%">登录</el-button>
        </el-form-item>

      </el-form>
    </el-card>


  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '../stores/app'
import http from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const store = useAppStore()
const loading = ref(false)

const form = reactive({ username: '', password: '' })

async function handleLogin() {
  loading.value = true
  try {
    const res = await http.post('/auth/login', { username: form.username, password: form.password })
    store.login(res.access_token, res.username, res.role)
    ElMessage.success('登录成功')
    router.push(route.query.redirect || '/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper { display:flex; justify-content:center; align-items:center; height:100vh; background:#f0f2f5; }
.login-card { width:380px; }
.login-card h2 { text-align:center; margin-bottom:24px; }
</style>
