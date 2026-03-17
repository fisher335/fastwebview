<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '提示'
  },
  message: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'info', // info, success, error, confirm
    validator: (value) => ['info', 'success', 'error', 'confirm'].includes(value)
  }
})

const emit = defineEmits(['confirm', 'cancel', 'update:show'])

const showDialog = ref(props.show)

watch(() => props.show, (newVal) => {
  showDialog.value = newVal
})

watch(showDialog, (newVal) => {
  emit('update:show', newVal)
})

function confirm() {
  emit('confirm')
  closeDialog()
}

function cancel() {
  emit('cancel')
  closeDialog()
}

function closeDialog() {
  showDialog.value = false
}

function getIcon() {
  switch (props.type) {
    case 'success': return '✓'
    case 'error': return '✗'
    case 'confirm': return '?'
    default: return 'i'
  }
}

function getIconColor() {
  switch (props.type) {
    case 'success': return '#4caf50'
    case 'error': return '#f44336'
    case 'confirm': return '#ff9800'
    default: return '#2196f3'
  }
}
</script>

<template>
  <div v-if="showDialog" class="dialog-overlay" @click.self="type === 'confirm' ? cancel() : closeDialog()">
    <div class="dialog">
      <div class="dialog-header">
        <div class="dialog-icon" :style="{ backgroundColor: getIconColor() }">
          {{ getIcon() }}
        </div>
        <h3 class="dialog-title">{{ title }}</h3>
        <button class="dialog-close" @click="type === 'confirm' ? cancel() : closeDialog()">×</button>
      </div>
      
      <div class="dialog-body">
        <p class="dialog-message">{{ message }}</p>
      </div>
      
      <div class="dialog-footer">
        <template v-if="type === 'confirm'">
          <button class="dialog-btn dialog-btn-cancel" @click="cancel">取消</button>
          <button class="dialog-btn dialog-btn-confirm" @click="confirm">确定</button>
        </template>
        <template v-else>
          <button class="dialog-btn dialog-btn-ok" @click="closeDialog">确定</button>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.dialog {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 400px;
  overflow: hidden;
  animation: slideIn 0.3s ease;
}

.dialog-header {
  display: flex;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
  position: relative;
}

.dialog-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 18px;
  margin-right: 12px;
  flex-shrink: 0;
}

.dialog-title {
  margin: 0;
  font-size: 18px;
  color: #333;
  flex-grow: 1;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.dialog-close:hover {
  background-color: #f5f5f5;
  color: #666;
}

.dialog-body {
  padding: 24px 20px;
}

.dialog-message {
  margin: 0;
  font-size: 16px;
  line-height: 1.5;
  color: #555;
  word-break: break-word;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #eee;
}

.dialog-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 80px;
}

.dialog-btn-ok {
  background-color: #007bff;
  color: white;
}

.dialog-btn-ok:hover {
  background-color: #0056b3;
}

.dialog-btn-confirm {
  background-color: #007bff;
  color: white;
}

.dialog-btn-confirm:hover {
  background-color: #0056b3;
}

.dialog-btn-cancel {
  background-color: #f5f5f5;
  color: #666;
}

.dialog-btn-cancel:hover {
  background-color: #e0e0e0;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>