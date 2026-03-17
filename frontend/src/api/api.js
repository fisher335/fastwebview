import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export async function scanNetworks() {
  try {
    const response = await api.get('/wifi/scan')
    return { success: true, data: response.data }
  } catch (err) {
    return { 
      success: false, 
      error: '扫描失败: ' + (err.response?.data?.detail || err.message)
    }
  }
}

export async function jamNetwork(bssid, count = 10) {
  try {
    const response = await api.post('/wifi/jam', null, {
      params: { bssid, count }
    })
    return { success: true, data: response.data }
  } catch (err) {
    return { 
      success: false, 
      error: '阻断失败: ' + (err.response?.data?.detail || err.message)
    }
  }
}