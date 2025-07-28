<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <NuxtLink to="/" class="text-xl font-bold text-gray-900">
              Boiler App
            </NuxtLink>
          </div>
          
          <div class="flex items-center space-x-4">
            <template v-if="isAuthenticated">
              <span class="text-gray-700">Hello, {{ fullName }}</span>
              <NuxtLink
                to="/dashboard"
                class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Dashboard
              </NuxtLink>
              <button
                @click="handleLogout"
                class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </template>
            <template v-else>
              <NuxtLink
                to="/login"
                class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Login
              </NuxtLink>
              <NuxtLink
                to="/register"
                class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Register
              </NuxtLink>
            </template>
          </div>
        </div>
      </div>
    </nav>
    
    <main>
      <slot />
    </main>
  </div>
</template>

<script setup>
const authStore = useAuthStore()
const { isAuthenticated, fullName } = storeToRefs(authStore)

const handleLogout = async () => {
  await authStore.logout()
}

// Check authentication on mount
onMounted(() => {
  authStore.checkAuth()
})
</script>