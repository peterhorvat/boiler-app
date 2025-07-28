<template>
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <div class="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <div class="text-center">
          <h1 class="text-3xl font-bold text-gray-900 mb-4">
            Welcome to your Dashboard
          </h1>
          <p class="text-lg text-gray-600 mb-8">
            Hello {{ fullName }}! You have successfully authenticated.
          </p>
          
          <div class="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div class="bg-white p-6 rounded-lg shadow">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Profile</h3>
              <p class="text-gray-600 mb-4">Manage your account settings</p>
              <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
                Edit Profile
              </button>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Settings</h3>
              <p class="text-gray-600 mb-4">Configure your preferences</p>
              <button 
                @click="showChangePassword = true"
                class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded"
              >
                Change Password
              </button>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">Analytics</h3>
              <p class="text-gray-600 mb-4">View your activity stats</p>
              <button class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded">
                View Stats
              </button>
            </div>
          </div>
          
          <div class="mt-8 bg-white p-6 rounded-lg shadow max-w-2xl mx-auto">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">User Information</h3>
            <div class="space-y-2 text-left">
              <p><strong>Username:</strong> {{ user?.username }}</p>
              <p><strong>Email:</strong> {{ user?.email }}</p>
              <p><strong>Full Name:</strong> {{ fullName }}</p>
              <p><strong>Verified:</strong> {{ user?.is_verified ? 'Yes' : 'No' }}</p>
              <p><strong>Member Since:</strong> {{ formatDate(user?.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Change Password Modal -->
    <div v-if="showChangePassword" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Change Password</h3>
          <form @submit.prevent="handlePasswordChange">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Current Password</label>
                <input
                  v-model="passwordForm.old_password"
                  type="password"
                  required
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">New Password</label>
                <input
                  v-model="passwordForm.new_password"
                  type="password"
                  required
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Confirm New Password</label>
                <input
                  v-model="passwordForm.new_password_confirm"
                  type="password"
                  required
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            
            <div v-if="passwordError" class="text-red-600 text-sm mt-2">
              {{ passwordError }}
            </div>
            
            <div class="flex justify-end space-x-3 mt-6">
              <button
                type="button"
                @click="showChangePassword = false"
                class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="loading"
                class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                <span v-if="loading">Changing...</span>
                <span v-else>Change Password</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  middleware: 'auth'
})

const authStore = useAuthStore()
const { user, fullName, loading } = storeToRefs(authStore)

const showChangePassword = ref(false)
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  new_password_confirm: ''
})
const passwordError = ref('')

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const handlePasswordChange = async () => {
  passwordError.value = ''
  
  const result = await authStore.changePassword(passwordForm)
  
  if (result.success) {
    showChangePassword.value = false
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.new_password_confirm = ''
    // You could add a success toast here
  } else {
    passwordError.value = typeof result.error === 'object' 
      ? Object.values(result.error)[0]?.[0] || 'Password change failed'
      : result.error
  }
}
</script>