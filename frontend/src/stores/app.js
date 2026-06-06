import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || '',
    role: localStorage.getItem('role') || '',
    currentCluster: null,
  }),
  getters: {
    isAdmin: (state) => state.role === 'admin',
  },
  actions: {
    login(token, username, role) {
      this.token = token
      this.username = username
      this.role = role
      localStorage.setItem('token', token)
      localStorage.setItem('username', username)
      localStorage.setItem('role', role)
    },
    logout() {
      this.token = ''
      this.username = ''
      this.role = ''
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
    },
    setCurrentCluster(cluster) {
      this.currentCluster = cluster
    },
  },
})