import { ref, computed } from 'vue'
import { useWebSocket } from './useWebSocket'
import { useAuthStore } from '~/stores/auth'

interface ChatMessage {
  id: string
  type: 'chat_message' | 'user_joined' | 'user_left' | 'system'
  message: string
  user: string
  user_id: number
  timestamp: string
}

interface ChatUser {
  id: number
  username: string
  isOnline: boolean
}

export const useChat = (roomName: string) => {
  const authStore = useAuthStore()
  const messages = ref<ChatMessage[]>([])
  const users = ref<ChatUser[]>([])
  const isTyping = ref<string[]>([])

  const wsUrl = `ws/chat/${roomName}/`

  const {
    isConnected,
    isConnecting,
    lastMessage,
    connectionError,
    connect,
    disconnect,
    send
  } = useWebSocket(wsUrl)

  // Watch for new chat messages
  watch(lastMessage, (message) => {
    if (!message) return

    switch (message.type) {
      case 'chat_message':
        const chatMessage: ChatMessage = {
          id: Date.now().toString(),
          type: message.type,
          message: message.message,
          user: message.user,
          user_id: message.user_id,
          timestamp: message.timestamp || new Date().toISOString()
        }
        messages.value.push(chatMessage)
        
        // Keep only last 100 messages
        if (messages.value.length > 100) {
          messages.value = messages.value.slice(-100)
        }
        break

      case 'user_joined':
        const existingUser = users.value.find(u => u.id === message.user_id)
        if (!existingUser) {
          users.value.push({
            id: message.user_id,
            username: message.user,
            isOnline: true
          })
        } else {
          existingUser.isOnline = true
        }
        
        // Add system message
        messages.value.push({
          id: Date.now().toString(),
          type: 'system',
          message: `${message.user} joined the chat`,
          user: 'System',
          user_id: 0,
          timestamp: new Date().toISOString()
        })
        break

      case 'user_left':
        const userIndex = users.value.findIndex(u => u.id === message.user_id)
        if (userIndex > -1) {
          users.value[userIndex].isOnline = false
        }
        
        // Add system message
        messages.value.push({
          id: Date.now().toString(),
          type: 'system',
          message: `${message.user} left the chat`,
          user: 'System',
          user_id: 0,
          timestamp: new Date().toISOString()
        })
        break

      case 'typing_start':
        if (!isTyping.value.includes(message.user) && message.user !== authStore.user?.username) {
          isTyping.value.push(message.user)
        }
        break

      case 'typing_stop':
        const typingIndex = isTyping.value.indexOf(message.user)
        if (typingIndex > -1) {
          isTyping.value.splice(typingIndex, 1)
        }
        break
    }
  })

  const sendMessage = (message: string) => {
    if (!message.trim()) return false

    return send({
      type: 'chat_message',
      message: message.trim()
    })
  }

  const sendTypingStart = () => {
    send({
      type: 'typing_start'
    })
  }

  const sendTypingStop = () => {
    send({
      type: 'typing_stop'
    })
  }

  const onlineUsers = computed(() => {
    return users.value.filter(u => u.isOnline)
  })

  const typingUsersText = computed(() => {
    if (isTyping.value.length === 0) return ''
    if (isTyping.value.length === 1) return `${isTyping.value[0]} is typing...`
    if (isTyping.value.length === 2) return `${isTyping.value[0]} and ${isTyping.value[1]} are typing...`
    return `${isTyping.value.length} users are typing...`
  })

  const clearMessages = () => {
    messages.value = []
  }

  return {
    messages: readonly(messages),
    users: readonly(users),
    onlineUsers: readonly(onlineUsers),
    isTyping: readonly(isTyping),
    typingUsersText: readonly(typingUsersText),
    isConnected: readonly(isConnected),
    isConnecting: readonly(isConnecting),
    connectionError: readonly(connectionError),
    sendMessage,
    sendTypingStart,
    sendTypingStop,
    clearMessages,
    connect,
    disconnect
  }
}