<template>
  <div>
    <h3>节点管理</h3>
    <div style="margin:16px 0">
      <el-select v-model="selectedCluster" placeholder="选择集群" @change="fetchData" style="width:200px">
        <el-option v-for="c in clusters" :key="c.id" :value="c.id" :label="c.name" />
      </el-select>
    </div>
    <el-table :data="nodes" v-loading="loading">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'Ready' ? 'success' : 'danger'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="roles" label="角色" width="100" />
      <el-table-column prop="version" label="版本" width="100" />
      <el-table-column prop="internal_ip" label="内部 IP" width="140" />
      <el-table-column prop="age" label="运行时间" width="80" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../../api'

const clusters = ref([])
const selectedCluster = ref(null)
const nodes = ref([])
const loading = ref(false)

async function fetchClusters() {
  clusters.value = await http.get('/clusters')
  if (clusters.value.length) {
    selectedCluster.value = clusters.value[0].id
    await fetchData()
  }
}

async function fetchData() {
  if (!selectedCluster.value) return
  loading.value = true
  try { nodes.value = await http.get(`/k8s/${selectedCluster.value}/nodes`) } finally { loading.value = false }
}

onMounted(fetchClusters)
</script>
