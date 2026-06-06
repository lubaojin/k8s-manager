<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h3 style="margin:0">仪表盘</h3>
      <el-button text @click="fetchData" :loading="loading">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
    </div>

    <!-- 四大核心指标 -->
    <el-row :gutter="16">
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-value" style="color:#409EFF">{{ summary.clusters }}</div>
          <div class="metric-label">集群</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-value" style="color:#67c23a">{{ summary.nodes }}</div>
          <div class="metric-label">节点</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-value" style="color:#67c23a">{{ summary.pods_running }}<span class="metric-unit"> / {{ summary.pods_total }}</span></div>
          <div class="metric-label">Pods Running</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="metric-card">
          <div class="metric-value" :style="{color: (summary.pods_failed + summary.pods_pending) > 0 ? '#f56c6c' : '#67c23a'}">
            {{ summary.pods_failed + summary.pods_pending }}
          </div>
          <div class="metric-label">Pods 异常</div>
        </div>
      </el-col>
    </el-row>

    <!-- 集群列表 -->
    <el-card shadow="never" style="margin-top:16px">
      <template #header><strong>集群</strong></template>
      <el-table :data="clusters" size="small" v-if="clusters.length" @row-click="(row) => $router.push(`/clusters/${row.cluster_id}`)" style="cursor:pointer">
        <el-table-column prop="cluster_name" label="名称" />
        <el-table-column label="状态" width="90">
          <template #default="{row}">
            <el-tag :type="row.cluster_status === 'connected' ? 'success' : 'danger'" size="small">
              {{ row.cluster_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="namespaces" label="命名空间" width="90" align="center" />
        <el-table-column prop="nodes" label="节点" width="70" align="center" />
        <el-table-column label="Pods" width="160" align="center">
          <template #default="{row}">
            <span style="color:#67c23a">{{ row.pods_running }}</span>
            <template v-if="row.pods_pending"> / <span style="color:#e6a23c">{{ row.pods_pending }}</span></template>
            <template v-if="row.pods_failed"> / <span style="color:#f56c6c">{{ row.pods_failed }}</span></template>
            <span style="color:#909399"> / {{ row.pods_total }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{row}">
            <el-button text size="small" type="primary">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无集群" :image-size="60" />
    </el-card>

    <!-- 节点资源 -->
    <el-card shadow="never" style="margin-top:16px">
      <template #header><strong>节点资源</strong></template>
      <el-table :data="allNodes" size="small" v-if="allNodes.length">
        <el-table-column prop="name" label="节点" width="140" />
        <el-table-column label="状态" width="90">
          <template #default="{row}">
            <el-tag :type="row.status === 'Ready' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="CPU" min-width="200">
          <template #default="{row}">
            <div style="display:flex;align-items:center;gap:8px">
              <span style="font-size:12px;color:#909399;width:70px;text-align:right">
                {{ row.cpu_usage != null ? row.cpu_usage.toFixed(1) + ' / ' + row.capacity_cpu : row.capacity_cpu }} 核
              </span>
              <el-progress
                :percentage="row.cpu_usage != null ? Math.min((row.cpu_usage / row.capacity_cpu) * 100, 100) : 0"
                :stroke-width="14"
                :show-text="false"
                :color="cpuColor(row.cpu_usage, row.capacity_cpu)"
                style="flex:1"
              />
              <span v-if="row.cpu_pct != null" style="font-size:12px;color:#909399;width:40px">{{ row.cpu_pct }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="内存" min-width="200">
          <template #default="{row}">
            <div style="display:flex;align-items:center;gap:8px">
              <span style="font-size:12px;color:#909399;width:80px;text-align:right">
                {{ row.mem_usage != null ? formatMem(row.mem_usage) + ' / ' + formatMem(row.capacity_mem) : formatMem(row.capacity_mem) }}
              </span>
              <el-progress
                :percentage="row.mem_usage != null ? Math.min((row.mem_usage / row.capacity_mem) * 100, 100) : 0"
                :stroke-width="14"
                :show-text="false"
                :color="memColor(row.mem_usage, row.capacity_mem)"
                style="flex:1"
              />
              <span v-if="row.mem_pct != null" style="font-size:12px;color:#909399;width:40px">{{ row.mem_pct }}%</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="无节点数据" :image-size="60" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import http from '../api'

const loading = ref(false)
const clusters = ref([])
const allNodes = ref([])
const summary = ref({ clusters: 0, namespaces: 0, nodes: 0, pods_total: 0, pods_running: 0, pods_pending: 0, pods_failed: 0 })

function formatMem(bytes) {
  if (!bytes) return '0'
  if (bytes >= 1024**3) return (bytes / 1024**3).toFixed(1) + ' GiB'
  if (bytes >= 1024**2) return (bytes / 1024**2).toFixed(0) + ' MiB'
  return bytes + ' B'
}

function cpuColor(usage, capacity) {
  if (usage == null) return '#909399'
  const pct = usage / capacity
  if (pct > 0.8) return '#f56c6c'
  if (pct > 0.5) return '#e6a23c'
  return '#67c23a'
}

function memColor(usage, capacity) {
  if (usage == null) return '#909399'
  const pct = usage / capacity
  if (pct > 0.8) return '#f56c6c'
  if (pct > 0.5) return '#e6a23c'
  return '#409EFF'
}

async function fetchData() {
  loading.value = true
  try {
    const res = await http.get('/clusters/dashboard')
    clusters.value = res.clusters || []
    summary.value = res.summary || {}
    allNodes.value = res.all_nodes || []
  } catch (e) {
    clusters.value = []
    summary.value = {}
    allNodes.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.metric-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
}
.metric-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
.metric-value { font-size: 36px; font-weight: 700; line-height: 1.2; }
.metric-unit { font-size: 16px; font-weight: 400; color: #909399; }
.metric-label { font-size: 13px; color: #909399; margin-top: 4px; }
</style>
