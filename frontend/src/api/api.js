import { ref } from 'vue'

let websocket = null
let reconnectTimer = null
const reconnectAttempts = ref(0)
const maxReconnectAttempts = 5

const messageHandlers = new Map()

export function onMessage(type, handler) {
  if (!messageHandlers.has(type)) {
    messageHandlers.set(type, [])
  }
  messageHandlers.get(type).push(handler)
}

export function offMessage(type, handler) {
  if (messageHandlers.has(type)) {
    const handlers = messageHandlers.get(type)
    const index = handlers.indexOf(handler)
    if (index > -1) {
      handlers.splice(index, 1)
    }
  }
}

function handleMessage(data) {
  const type = data.type
  if (messageHandlers.has(type)) {
    messageHandlers.get(type).forEach(handler => handler(data))
  }
}

export function connectWebSocket() {
  return new Promise((resolve, reject) => {
    const wsUrl = `ws://${window.location.host}/api/wifi/ws`
    
    websocket = new WebSocket(wsUrl)
    
    websocket.onopen = () => {
      console.log('WebSocket连接已建立')
      reconnectAttempts.value = 0
      resolve(websocket)
    }
    
    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleMessage(data)
      } catch (e) {
        console.error('解析WebSocket消息失败:', e)
      }
    }
    
    websocket.onerror = (error) => {
      console.error('WebSocket错误:', error)
      reject(error)
    }
    
    websocket.onclose = () => {
      console.log('WebSocket连接已关闭')
      attemptReconnect()
    }
  })
}

function attemptReconnect() {
  if (reconnectAttempts.value >= maxReconnectAttempts) {
    console.log('达到最大重连次数，停止重连')
    return
  }
  
  const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.value), 30000)
  console.log(`${delay}ms后尝试重连...`)
  
  reconnectTimer = setTimeout(() => {
    reconnectAttempts.value++
    connectWebSocket().catch(() => {})
  }, delay)
}

export function disconnectWebSocket() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
  }
  if (websocket) {
    websocket.close()
    websocket = null
  }
}

export function sendMessage(action, params = {}) {
  return new Promise((resolve, reject) => {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
      reject(new Error('WebSocket未连接'))
      return
    }
    
    const typeMap = {
      'scan': 'scan_result',
      'jam': 'jam_result'
    }
    const responseType = typeMap[action] || 'scan_result'
    
    const handler = (data) => {
      if (data.type === responseType || data.type === 'error') {
        offMessage(responseType, handler)
        offMessage('error', handler)
        
        if (data.type === 'error') {
          resolve({ success: false, error: data.message })
        } else if (data.type === 'jam_result') {
          if (data.data && data.data.status === 'error') {
            resolve({ success: false, error: data.data.message || '阻断失败' })
          } else {
            resolve({ success: true, data: data.data })
          }
        } else {
          resolve({ success: true, data: data.data })
        }
      }
    }
    
    onMessage(responseType, handler)
    onMessage('error', handler)
    
    websocket.send(JSON.stringify({
      action,
      params
    }))
  })
}

export async function scanNetworks() {
  try {
    return await sendMessage('scan', { interface: 'wlan0' })
  } catch (err) {
    return { success: false, error: '扫描失败: ' + err.message }
  }
}

export async function jamNetwork(bssid, count = 10) {
  try {
    return await sendMessage('jam', { bssid, count })
  } catch (err) {
    return { success: false, error: '阻断失败: ' + err.message }
  }
}

export function getConnectionState() {
  if (!websocket) return 'disconnected'
  switch (websocket.readyState) {
    case WebSocket.CONNECTING: return 'connecting'
    case WebSocket.OPEN: return 'connected'
    case WebSocket.CLOSING: return 'closing'
    case WebSocket.CLOSED: return 'disconnected'
    default: return 'unknown'
  }
}