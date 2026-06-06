<template>
  <div>
    <h3>服务网络</h3>
    <div style="display:flex;gap:12px;margin:16px 0">
      <el-select v-model="selectedCluster" placeholder="选择集群" @change="onClusterChange" style="width:200px">
        <el-option v-for="c in clusters" :key="c.id" :value="c.id" :label="c.name" />
      </el-select>
      <el-select v-model="ns" placeholder="命名空间" @change="fetchData" style="width:200px">
        <el-option value="all" label="ALL" />
        <el-option v-for="n in namespaces" :key="n.name" :value="n.name" :label="n.name" />
      </el-select>
    </div>
    <el-table :data="services" v-loading="loading">
      <el-table-column prop="namespace" label="命名空间" width="140" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="type" label="类型" width="120" />
      <el-table-column prop="cluster_ip" label="Cluster IP" width="140" />
      <el-table-column prop="ports" label="端口" width="140" />
      <el-table-column prop="age" label="运行时间" width="80" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../../api'

const clusters = ref([])
const namespaces = ref([])
const selectedCluster = ref(null)
const ns = ref('all')
const services = ref([])
const loading = ref(false)

async function fetchClusters() {
  clusters.value = await http.get('/clusters')
  if (clusters.value.length) {
    selectedCluster.value = clusters.value[0].id
    await onClusterChange()
  }
}

async function onClusterChange() {
  namespaces.value = await http.get(`/k8s/${selectedCluster.value}/namespaces`)
  ns.value = 'all'
  await fetchData()
}

async function fetchData() {
  if (!selectedCluster.value) return
  loading.value = true
  try {
    services.value = await http.get(`/k8s/${selectedCluster.value}/services`, { params: { namespace: ns.value } })
  } finally { loading.value = false }
}

onMounted(fetchClusters)
</script>
