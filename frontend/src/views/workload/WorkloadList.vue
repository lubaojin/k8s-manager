<template>
  <div>
    <h3>工作负载</h3>
    <div style="display:flex;gap:12px;margin:16px 0">
      <el-select v-model="selectedCluster" placeholder="选择集群" @change="onClusterChange" style="width:200px">
        <el-option v-for="c in clusters" :key="c.id" :value="c.id" :label="c.name" />
      </el-select>
      <el-select v-model="ns" placeholder="命名空间" @change="fetchData" style="width:200px">
        <el-option value="all" label="ALL" />
        <el-option v-for="n in namespaces" :key="n.name" :value="n.name" :label="n.name" />
      </el-select>
    </div>
    <el-tabs v-model="tab">
      <el-tab-pane label="Deployments" name="deployments">
        <el-table :data="deployments" v-loading="loading">
          <el-table-column prop="namespace" label="命名空间" width="140" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="replicas" label="副本" width="100" />
          <el-table-column label="就绪" width="80">
            <template #default="{ row }">
              <el-tag :type="row.ready ? 'success' : 'warning'">{{ row.ready ? '就绪' : '未就绪' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="age" label="运行时间" width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="Pods" name="pods">
        <el-table :data="pods" v-loading="loading">
          <el-table-column prop="namespace" label="命名空间" width="140" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="ready" label="就绪" width="80" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column prop="restarts" label="重启次数" width="80" />
          <el-table-column prop="node" label="节点" />
          <el-table-column prop="ip" label="IP" width="130" />
          <el-table-column prop="age" label="运行时间" width="80" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../../api'

const clusters = ref([])
const namespaces = ref([])
const selectedCluster = ref(null)
const ns = ref('all')
const tab = ref('deployments')
const deployments = ref([])
const pods = ref([])
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
    const [deps, p] = await Promise.all([
      http.get(`/k8s/${selectedCluster.value}/deployments`, { params: { namespace: ns.value } }),
      http.get(`/k8s/${selectedCluster.value}/pods`, { params: { namespace: ns.value } }),
    ])
    deployments.value = deps
    pods.value = p
  } finally { loading.value = false }
}

onMounted(fetchClusters)
</script>
