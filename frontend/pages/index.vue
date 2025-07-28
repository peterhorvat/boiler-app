<template>
  <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900 mb-8">
        Welcome to Boiler App
      </h1>
      <p class="text-xl text-gray-600 mb-12">
        A modern web application with Django REST API and Nuxt 3 frontend
      </p>
      
      <div class="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">Backend Features</h2>
          <ul class="text-left text-gray-600 space-y-2">
            <li>✅ Django REST Framework</li>
            <li>✅ JWT Authentication</li>
            <li>✅ PostgreSQL Database</li>
            <li>✅ Redis Caching</li>
            <li>✅ Celery Task Queue</li>
            <li>✅ Docker Ready</li>
          </ul>
        </div>
        
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">Frontend Features</h2>
          <ul class="text-left text-gray-600 space-y-2">
            <li>✅ Nuxt 3 Framework</li>
            <li>✅ Vue 3 Composition API</li>
            <li>✅ Pinia State Management</li>
            <li>✅ Tailwind CSS</li>
            <li>✅ Axios HTTP Client</li>
            <li>✅ TypeScript Support</li>
          </ul>
        </div>
      </div>
      
      <div class="mt-12">
        <template v-if="!isAuthenticated">
          <NuxtLink
            to="/register"
            class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg mr-4"
          >
            Get Started
          </NuxtLink>
          <NuxtLink
            to="/login"
            class="bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-lg"
          >
            Login
          </NuxtLink>
        </template>
        <template v-else>
          <NuxtLink
            to="/dashboard"
            class="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg"
          >
            Go to Dashboard
          </NuxtLink>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
const authStore = useAuthStore()
const { isAuthenticated } = storeToRefs(authStore)
</script>