<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h3>用户管理</h3>
      <el-button v-if="store.isAdmin" type="primary" @click="openAdd">添加用户</el-button>
    </div>

    <el-table :data="users" style="margin-top:16px" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="email" label="邮箱" width="200" />
      <el-table-column prop="role" label="角色" width="100" />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button v-if="store.isAdmin" size="small" @click="openEdit(row)">编辑</el-button>
          <el-button v-if="store.isAdmin" size="small" type="danger" @click="removeUser(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editing ? '编辑用户' : '添加用户'" width="460px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" :disabled="editing" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item v-if="!editing" label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item v-if="editing" label="新密码">
          <el-input v-model="form.password" type="password" show-password placeholder="留空则不修改" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option value="admin" label="管理员" />
            <el-option value="viewer" label="观察者" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="editing" label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAppStore } from '../../stores/app'
import http from '../../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useAppStore()
const users = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editing = ref(false)
const saving = ref(false)
const editingId = ref(null)

const form = reactive({ username: '', email: '', password: '', role: 'viewer', is_active: true })

async function fetchUsers() {
  loading.value = true
  try { users.value = await http.get('/auth/users') } finally { loading.value = false }
}

function openAdd() {
  editing.value = false
  editingId.value = null
  form.username = ''
  form.email = ''
  form.password = ''
  form.role = 'viewer'
  form.is_active = true
  dialogVisible.value = true
}

function openEdit(row) {
  editing.value = true
  editingId.value = row.id
  form.username = row.username
  form.email = row.email || ''
  form.password = ''
  form.role = row.role
  form.is_active = row.is_active
  dialogVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    if (editing.value) {
      const patchData = {
        email: form.email || null,
        role: form.role,
        is_active: form.is_active,
      }
      if (form.password) {
        patchData.password = form.password
      }
      await http.patch(`/auth/users/${editingId.value}`, patchData)
      ElMessage.success('用户已更新')
    } else {
      await http.post('/auth/register', {
        username: form.username,
        email: form.email || null,
        password: form.password,
        role: form.role,
      })
      ElMessage.success('用户已创建')
    }
    dialogVisible.value = false
    await fetchUsers()
  } finally {
    saving.value = false
  }
}

async function removeUser(row) {
  await ElMessageBox.confirm(`确定删除用户 "${row.username}"？`, '确认')
  await http.delete(`/auth/users/${row.id}`)
  ElMessage.success('已删除')
  await fetchUsers()
}

onMounted(fetchUsers)
</script>
