import { ref, onUnmounted, computed } from 'vue'
import { useAuthStore } from '~/stores/auth'

interface WebSocketMessage {
  type: string
  message?: string
  timestamp?: string
  [key: string]: any
}

interface WebSocketOptions {
  reconnectInterval?: number
  maxReconnectAttempts?: number
  heartbeatInterval?: number
}

export const useWebSocket = (url: string, options: WebSocketOptions = {}) => {
  const {
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    heartbeatInterval = 30000
  } = options

  const authStore = useAuthStore()
  const config = useRuntimeConfig()

  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const lastMessage = ref<WebSocketMessage | null>(null)
  const messages = ref<WebSocketMessage[]>([])
  const connectionError = ref<string | null>(null)

  let reconnectAttempts = 0
  let heartbeatTimer: NodeJS.Timeout | null = null
  let reconnectTimer: NodeJS.Timeout | null = null

  const wsUrl = computed(() => {
    const baseUrl = config.public.apiBaseUrl.replace('http', 'ws')
    const token = useCookie('access_token').value
    return `${baseUrl.replace('/api', '')}/${url}?token=${token}`
  })

  const connect = () => {
    if (isConnecting.value || isConnected.value) return

    if (!authStore.isAuthenticated) {
      connectionError.value = 'User not authenticated'
      return
    }

    try {
      isConnecting.value = true
      connectionError.value = null

      ws.value = new WebSocket(wsUrl.value)

      ws.value.onopen = () => {
        isConnected.value = true
        isConnecting.value = false
        reconnectAttempts = 0
        connectionError.value = null
        startHeartbeat()
        console.log(`WebSocket connected to ${url}`)
      }

      ws.value.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          lastMessage.value = message
          messages.value.push(message)
          
          // Keep only last 100 messages in memory
          if (messages.value.length > 100) {
            messages.value = messages.value.slice(-100)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.value.onclose = (event) => {
        isConnected.value = false
        isConnecting.value = false
        stopHeartbeat()

        if (event.code !== 1000) { // Not a normal closure
          console.log(`WebSocket closed unexpectedly: ${event.code} ${event.reason}`)
          attemptReconnect()
        }
      }

      ws.value.onerror = (error) => {
        console.error('WebSocket error:', error)
        connectionError.value = 'Connection error occurred'
        isConnecting.value = false
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      connectionError.value = 'Failed to establish connection'
      isConnecting.value = false
    }
  }

  const disconnect = () => {
    stopHeartbeat()
    clearReconnectTimer()
    
    if (ws.value) {
      ws.value.close(1000, 'Manual disconnect')
      ws.value = null
    }
    
    isConnected.value = false
    isConnecting.value = false
  }

  const send = (message: any) => {
    if (!isConnected.value || !ws.value) {
      console.warn('WebSocket not connected, cannot send message')
      return false
    }

    try {
      const messageStr = typeof message === 'string' ? message : JSON.stringify(message)
      ws.value.send(messageStr)
      return true
    } catch (error) {
      console.error('Failed to send WebSocket message:', error)
      return false
    }
  }

  const attemptReconnect = () => {
    if (reconnectAttempts >= maxReconnectAttempts) {
      connectionError.value = `Max reconnection attempts (${maxReconnectAttempts}) reached`
      return
    }

    reconnectAttempts++
    console.log(`Attempting to reconnect... (${reconnectAttempts}/${maxReconnectAttempts})`)

    reconnectTimer = setTimeout(() => {
      connect()
    }, reconnectInterval)
  }

  const startHeartbeat = () => {
    heartbeatTimer = setInterval(() => {
      if (isConnected.value) {
        send({
          type: 'ping',
          timestamp: new Date().toISOString()
        })
      }
    }, heartbeatInterval)
  }

  const stopHeartbeat = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  const clearReconnectTimer = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  const clearMessages = () => {
    messages.value = []
    lastMessage.value = null
  }

  // Auto-connect when composable is used
  connect()

  // Cleanup on unmount
  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected: readonly(isConnected),
    isConnecting: readonly(isConnecting),
    lastMessage: readonly(lastMessage),
    messages: readonly(messages),
    connectionError: readonly(connectionError),
    connect,
    disconnect,
    send,
    clearMessages
  }
}