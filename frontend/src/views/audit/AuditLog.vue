<template>
  <div>
    <h3>审计日志</h3>
    <el-table :data="logs" v-loading="loading" style="margin-top:16px" max-height="600">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户" width="100" />
      <el-table-column prop="action" label="操作" width="80" />
      <el-table-column prop="resource_type" label="资源类型" width="100" />
      <el-table-column prop="resource_name" label="资源名" width="150" />
      <el-table-column prop="cluster_name" label="集群" width="120" />
      <el-table-column prop="namespace" label="命名空间" width="120" />
      <el-table-column prop="result" label="结果" width="80">
        <template #default="{ row }">
          <el-tag :type="row.result === 'success' ? 'success' : 'danger'" size="small">{{ row.result }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="160" />
      <el-table-column prop="detail" label="详情" min-width="150" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../../api'

const logs = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    logs.value = await http.get('/audit')
  } catch (e) {
    /* skip */
  } finally {
    loading.value = false
  }
})
</script>
