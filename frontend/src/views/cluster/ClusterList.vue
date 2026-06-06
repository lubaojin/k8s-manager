<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h3>集群管理</h3>
      <el-button v-if="store.isAdmin" type="primary" @click="showAdd = true">添加集群</el-button>
    </div>
    <el-table :data="clusters" style="margin-top:16px" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="environment" label="环境" width="80" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="version" label="版本" width="120" />
      <el-table-column prop="node_count" label="节点数" width="80" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/clusters/${row.id}`)">详情</el-button>
          <el-button v-if="store.isAdmin" size="small" type="danger" @click="removeCluster(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showAdd" title="添加集群" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" />
        </el-form-item>
        <el-form-item label="环境">
          <el-select v-model="form.environment">
            <el-option value="dev" label="开发" />
            <el-option value="staging" label="预发布" />
            <el-option value="prod" label="生产" />
          </el-select>
        </el-form-item>
        <el-form-item label="Kubeconfig">
          <el-input v-model="form.kubeconfig" type="textarea" :rows="6" placeholder="粘贴 kubeconfig YAML" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addCluster" :loading="adding">保存</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAppStore } from '../../stores/app'
import http from '../../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useAppStore()
const clusters = ref([])
const loading = ref(false)
const showAdd = ref(false)
const adding = ref(false)

const form = reactive({ name: '', description: '', environment: 'dev', kubeconfig: '' })

async function fetchClusters() {
  loading.value = true
  try { clusters.value = await http.get('/clusters') } finally { loading.value = false }
}

async function addCluster() {
  adding.value = true
  try {
    await http.post('/clusters', { ...form })
    ElMessage.success('集群添加成功')
    showAdd.value = false
    await fetchClusters()
  } finally { adding.value = false }
}

async function removeCluster(row) {
  await ElMessageBox.confirm(`确定删除集群 "${row.name}"？`, '确认')
  await http.delete(`/clusters/${row.id}`)
  ElMessage.success('已删除')
  await fetchClusters()
}

function statusTagType(status) {
  const map = {
    connected: 'success',
    error: 'danger',
    unknown: 'info',
  }
  return map[status] || 'info'
}

onMounted(fetchClusters)
</script>
