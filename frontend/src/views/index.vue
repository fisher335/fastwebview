<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { 
  scanNetworks as apiScan, 
  jamNetwork as apiJam,
  connectWebSocket,
  disconnectWebSocket,
  getConnectionState,
  onMessage
} from '../api/api.js'
import Dialog from '../components/Dialog.vue'

const networks = ref([])
const loading = ref(false)
const jamming = ref(false)
const error = ref(null)
const expandedRows = ref(new Set())
const connectionStatus = ref('disconnected')

// Dialog state
const dialogShow = ref(false)
const dialogTitle = ref('提示')
const dialogMessage = ref('')
const dialogType = ref('info')
const currentBssid = ref('')

function toggleRow(bssid) {
  if (expandedRows.value.has(bssid)) {
    expandedRows.value.delete(bssid)
  } else {
    expandedRows.value.add(bssid)
  }
}

function isRowExpanded(bssid) {
  return expandedRows.value.has(bssid)
}

async function initConnection() {
  connectionStatus.value = 'connecting'
  try {
    await connectWebSocket()
    connectionStatus.value = 'connected'
    scanNetworks()
  } catch (err) {
    connectionStatus.value = 'error'
    error.value = 'WebSocket连接失败，请刷新页面重试'
  }
}

async function scanNetworks() {
  loading.value = true
  error.value = null
  const result = await apiScan()
  if (result.success) {
    networks.value = result.data
  } else {
    error.value = result.error
  }
  loading.value = false
}

async function jamNetwork(bssid) {
  currentBssid.value = bssid
  showConfirmDialog(`确定要阻断网络 ${bssid} 吗？`)
}

async function confirmJam() {
  jamming.value = true
  const result = await apiJam(currentBssid.value, 10)
  if (result.success) {
    showMessageDialog('阻断成功', `阻断操作已发送: ${JSON.stringify(result.data)}`, 'success')
  } else {
    showMessageDialog('阻断失败', result.error, 'error')
  }
  jamming.value = false
}

function showConfirmDialog(message) {
  dialogTitle.value = '确认操作'
  dialogMessage.value = message
  dialogType.value = 'confirm'
  dialogShow.value = true
}

function showMessageDialog(title, message, type = 'info') {
  dialogTitle.value = title
  dialogMessage.value = message
  dialogType.value = type
  dialogShow.value = true
}

function onDialogConfirm() {
  if (dialogType.value === 'confirm') {
    confirmJam()
  }
}

function onDialogCancel() {
  // 取消操作
}

function getEncryptionColor(encryption) {
  switch (encryption) {
    case 'WPA2': return '#4caf50'
    case 'WPA': return '#ff9800'
    case 'WEP': return '#f44336'
    case 'OPEN': return '#2196f3'
    default: return '#9e9e9e'
  }
}

function getSignalColor(strength) {
  if (strength >= -50) return '#4caf50'
  if (strength >= -60) return '#8bc34a'
  if (strength >= -70) return '#ff9800'
  return '#f44336'
}

onMounted(() => {
  initConnection()
})

onUnmounted(() => {
  disconnectWebSocket()
})
</script>

<template>
  <div class="container">
    <header>
      <h1>WiFi 扫描与阻断工具</h1>
<!--      <p>扫描附近的WiFi网络并进行阻断测试</p>-->
      <p></p>
    </header>

    <div class="controls">
      <div class="left-controls">
        <button @click="scanNetworks" :disabled="loading || connectionStatus !== 'connected'" class="btn btn-primary">
          {{ loading ? '扫描中...' : '扫描网络' }}
        </button>
        <span class="network-count">发现 {{ networks.length }} 个网络</span>
      </div>
      <div class="connection-status">
        <span class="status-dot" :class="connectionStatus"></span>
        <span class="status-text">
          {{ connectionStatus === 'connected' ? '已连接' : connectionStatus === 'connecting' ? '连接中...' : '未连接' }}
        </span>
      </div>
    </div>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div class="network-list">
      <table v-if="networks.length > 0">
        <thead>
          <tr>
            <th style="width: 30px;"></th>
            <th>SSID</th>
            <th>BSSID</th>
            <th>信道</th>
            <th>信号强度</th>
            <th>加密方式</th>
            <th>客户端</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="network in networks" :key="network.bssid">
            <tr class="ap-row" :class="{ expanded: isRowExpanded(network.bssid) }">
              <td>
                <button 
                  class="expand-btn" 
                  @click="toggleRow(network.bssid)"
                  v-if="network.clients && network.clients.length > 0"
                >
                  {{ isRowExpanded(network.bssid) ? '▼' : '▶' }}
                </button>
                <span v-else class="no-client">-</span>
              </td>
              <td class="ssid">{{ network.ssid || '隐藏网络' }}</td>
              <td class="bssid">{{ network.bssid }}</td>
              <td class="channel">{{ network.channel }}</td>
              <td class="signal">
                <div class="signal-bar">
                  <div class="signal-level" :style="{
                    width: Math.min(100, Math.max(0, (network.signal_strength + 100) * 2)) + '%',
                    backgroundColor: getSignalColor(network.signal_strength)
                  }"></div>
                </div>
                <span>{{ network.signal_strength }} dBm</span>
              </td>
              <td>
                <span class="encryption-badge" :style="{ backgroundColor: getEncryptionColor(network.encryption) }">
                  {{ network.encryption }}
                </span>
              </td>
              <td class="clients">{{ network.clients ? network.clients.length : 0 }}</td>
              <td>
                <button
                  @click="jamNetwork(network.bssid)"
                  :disabled="jamming"
                  class="btn btn-danger"
                >
                  阻断
                </button>
              </td>
            </tr>
            <tr v-if="isRowExpanded(network.bssid) && network.clients && network.clients.length > 0">
              <td colspan="8" class="sta-section">
                <div class="sta-list">
                  <div class="sta-title">已连接的客户端 (STA)</div>
                  <table class="sta-table">
                    <thead>
                      <tr>
                        <th>MAC地址</th>
                        <th>信号强度</th>
                        <th>数据包</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="client in network.clients" :key="client.mac">
                        <td class="mac">{{ client.mac }}</td>
                        <td>
                          <div class="signal-bar signal-bar-small">
                            <div class="signal-level" :style="{
                              width: Math.min(100, Math.max(0, (client.signal_strength + 100) * 2)) + '%',
                              backgroundColor: getSignalColor(client.signal_strength)
                            }"></div>
                          </div>
                          <span class="signal-text">{{ client.signal_strength }} dBm</span>
                        </td>
                        <td class="packets">{{ client.packets }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
      <div v-else class="empty">
        {{ loading ? '正在扫描...' : '未发现网络，点击扫描按钮开始扫描' }}
      </div>
    </div>

    <footer>
      <p>注意：阻断功能仅用于授权测试，请遵守当地法律法规。</p>
    </footer>

    <Dialog
      :show="dialogShow"
      :title="dialogTitle"
      :message="dialogMessage"
      :type="dialogType"
      @confirm="onDialogConfirm"
      @cancel="onDialogCancel"
      @update:show="dialogShow = $event"
    />
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

h1 {
  color: #333;
  margin-bottom: 10px;
}

.controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
  padding: 6px 12px;
  font-size: 14px;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c82333;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.network-count {
  font-weight: bold;
  color: #666;
}

.left-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.connected {
  background-color: #4caf50;
  box-shadow: 0 0 6px #4caf50;
}

.status-dot.connecting {
  background-color: #ff9800;
  animation: pulse 1s infinite;
}

.status-dot.disconnected,
.status-dot.error {
  background-color: #f44336;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.error {
  background-color: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid #f5c6cb;
}

.network-list table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 30px;
}

.network-list th {
  background-color: #f8f9fa;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
}

.network-list td {
  padding: 12px;
  border-bottom: 1px solid #dee2e6;
  vertical-align: middle;
}

.network-list tr:hover {
  background-color: #f8f9fa;
}

.ssid {
  font-weight: bold;
  color: #333;
}

.bssid {
  font-family: monospace;
  color: #666;
}

.signal {
  min-width: 150px;
}

.signal-bar {
  width: 100px;
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  display: inline-block;
  margin-right: 10px;
  vertical-align: middle;
}

.signal-level {
  height: 100%;
  border-radius: 4px;
}

.encryption-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  color: white;
  font-size: 12px;
  font-weight: bold;
  min-width: 60px;
  text-align: center;
}

.clients {
  text-align: center;
  font-weight: bold;
}

.empty {
  text-align: center;
  padding: 40px;
  color: #6c757d;
  font-size: 18px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

footer {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  text-align: center;
  color: #6c757d;
  font-size: 14px;
}

.expand-btn {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 12px;
  padding: 4px 8px;
}

.expand-btn:hover {
  color: #0056b3;
}

.no-client {
  color: #ccc;
}

.ap-row {
  transition: background-color 0.2s;
}

.ap-row.expanded {
  background-color: #e3f2fd;
}

.sta-section {
  padding: 0 !important;
  background-color: #f8f9fa;
}

.sta-list {
  padding: 15px;
}

.sta-title {
  font-weight: 600;
  color: #495057;
  margin-bottom: 10px;
  font-size: 14px;
}

.sta-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  border-radius: 6px;
  overflow: hidden;
}

.sta-table th,
.sta-table td {
  padding: 10px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.sta-table th {
  background-color: #e9ecef;
  font-weight: 600;
  font-size: 13px;
  color: #495057;
}

.sta-table td {
  font-size: 13px;
}

.sta-table tr:last-child td {
  border-bottom: none;
}

.sta-table .mac {
  font-family: monospace;
  color: #666;
}

.sta-table .signal {
  display: flex;
  align-items: center;
}

.signal-bar-small {
  width: 60px;
  height: 6px;
  margin-right: 8px;
}

.signal-text {
  font-size: 12px;
  color: #666;
}

.packets {
  text-align: right;
  font-family: monospace;
  color: #666;
}
</style>
