import { ref, computed } from 'vue'
import { useWebSocket } from './useWebSocket'
import { useAuthStore } from '~/stores/auth'

interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  message: string
  timestamp: string
  read: boolean
}

export const useNotifications = () => {
  const authStore = useAuthStore()
  const notifications = ref<Notification[]>([])

  const userId = computed(() => authStore.user?.id)
  const wsUrl = computed(() => `ws/notifications/${userId.value}/`)

  const {
    isConnected,
    isConnecting,
    lastMessage,
    connectionError,
    connect,
    disconnect,
    send
  } = useWebSocket(wsUrl.value)

  // Watch for new notification messages
  watch(lastMessage, (message) => {
    if (message && message.type === 'notification') {
      const notification: Notification = {
        id: Date.now().toString(),
        type: message.notification_type || 'info',
        message: message.message,
        timestamp: message.timestamp || new Date().toISOString(),
        read: false
      }
      
      notifications.value.unshift(notification)
      
      // Keep only last 50 notifications
      if (notifications.value.length > 50) {
        notifications.value = notifications.value.slice(0, 50)
      }
    }
  })

  const unreadCount = computed(() => {
    return notifications.value.filter(n => !n.read).length
  })

  const markAsRead = (notificationId: string) => {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.read = true
    }
  }

  const markAllAsRead = () => {
    notifications.value.forEach(n => n.read = true)
  }

  const removeNotification = (notificationId: string) => {
    const index = notifications.value.findIndex(n => n.id === notificationId)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearAll = () => {
    notifications.value = []
  }

  return {
    notifications: readonly(notifications),
    unreadCount: readonly(unreadCount),
    isConnected: readonly(isConnected),
    isConnecting: readonly(isConnecting),
    connectionError: readonly(connectionError),
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
    connect,
    disconnect
  }
}