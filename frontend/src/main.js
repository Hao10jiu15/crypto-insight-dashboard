import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router' // 导入路由
import App from './App.vue'
import './assets/main.css' // 导入全局样式

const pinia = createPinia()
const app = createApp(App)

app.use(router) // 让Vue应用使用路由
app.use(pinia)
app.mount('#app')