<template>
  <div>
    <el-page-header @back="$router.push('/clusters')" title="返回">
      <template #content>{{ cluster?.name || '加载中...' }}</template>
    </el-page-header>

    <el-tabs v-model="activeTab" style="margin-top:16px">
      <el-tab-pane label="命名空间" name="namespaces">
        <el-table :data="namespaces" v-loading="loadingNs">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="status" label="状态" />
          <el-table-column prop="created_at" label="创建时间" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="Pods" name="pods">
        <div style="margin-bottom:8px">
          <el-select v-model="ns" placeholder="命名空间" @change="fetchPods" style="width:200px">
            <el-option value="all" label="ALL" />
            <el-option v-for="n in namespaces" :key="n.name" :value="n.name" :label="n.name" />
          </el-select>
        </div>
        <el-table :data="pods" v-loading="loadingPods">
          <el-table-column prop="namespace" label="命名空间" width="140" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="ready" label="就绪" width="80" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column prop="restarts" label="重启次数" width="80" />
          <el-table-column prop="node" label="节点" />
          <el-table-column prop="age" label="运行时间" width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="Deployments" name="deployments">
        <div style="margin-bottom:8px">
          <el-select v-model="depNs" placeholder="命名空间" @change="fetchDeployments" style="width:200px">
            <el-option value="all" label="ALL" />
            <el-option v-for="n in namespaces" :key="n.name" :value="n.name" :label="n.name" />
          </el-select>
        </div>
        <el-table :data="deployments" v-loading="loadingDeps">
          <el-table-column prop="namespace" label="命名空间" width="140" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="replicas" label="副本" width="100" />
          <el-table-column label="就绪" width="80">
            <template #default="{ row }">
              <el-tag :type="row.ready ? 'success' : 'warning'">{{ row.ready ? '是' : '否' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="age" label="运行时间" width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="Events" name="events">
        <el-table :data="events" v-loading="loadingEv" max-height="500">
          <el-table-column prop="type" label="类型" width="80">
            <template #default="{ row }">
              <el-tag :type="row.type === 'Warning' ? 'danger' : ''" size="small">{{ row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="原因" width="150" />
          <el-table-column prop="object_name" label="对象" width="200" />
          <el-table-column prop="message" label="消息" />
          <el-table-column prop="last_time" label="最后时间" width="160" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import http from '../../api'

const route = useRoute()
const clusterId = route.params.id
const cluster = ref(null)
const activeTab = ref('namespaces')
const namespaces = ref([])
const pods = ref([])
const deployments = ref([])
const events = ref([])
const ns = ref('all')
const depNs = ref('all')
const loadingNs = ref(false), loadingPods = ref(false), loadingDeps = ref(false), loadingEv = ref(false)

async function fetchCluster() {
  cluster.value = await http.get(`/clusters/${clusterId}`)
}

async function fetchNamespaces() {
  loadingNs.value = true
  try { namespaces.value = await http.get(`/k8s/${clusterId}/namespaces`) } finally { loadingNs.value = false }
}

async function fetchPods() {
  loadingPods.value = true
  try { pods.value = await http.get(`/k8s/${clusterId}/pods`, { params: { namespace: ns.value } }) } finally { loadingPods.value = false }
}

async function fetchDeployments() {
  loadingDeps.value = true
  try { deployments.value = await http.get(`/k8s/${clusterId}/deployments`, { params: { namespace: depNs.value } }) } finally { loadingDeps.value = false }
}

async function fetchEvents() {
  loadingEv.value = true
  try { events.value = await http.get(`/k8s/${clusterId}/events`, { params: { namespace: 'all' } }) } finally { loadingEv.value = false }
}

async function init() {
  await fetchCluster()
  await fetchNamespaces()
  ns.value = 'all'
  depNs.value = 'all'
  await Promise.all([fetchPods(), fetchDeployments(), fetchEvents()])
}

onMounted(init)
</script>
