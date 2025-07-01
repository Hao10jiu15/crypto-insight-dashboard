<script setup>
import { onMounted } from 'vue';
import { useMainStore } from '../../stores/mainStore';

const mainStore = useMainStore();

onMounted(() => {
    if (mainStore.currencies.length === 0) {
        mainStore.fetchCurrencies();
    }
});
</script>

<template>
    <aside class="app-sidebar">
      <h2>导航</h2>
      
      <!-- 主要页面导航 -->
      <div class="main-navigation">
        <router-link to="/" class="nav-link main-nav-link">
          📊 仪表板概览
        </router-link>
        <router-link to="/insights" class="nav-link main-nav-link">
          🧠 模型洞察分析
        </router-link>
      </div>

      <hr class="nav-divider">

      <!-- 货币列表 -->
      <h3>加密货币</h3>
      <div v-if="mainStore.isLoading">Loading...</div>
      <ul v-else class="navigation-list">
        <li v-for="currency in mainStore.currencies" :key="currency.id" class="nav-item-container">
          <router-link :to="`/currency/${currency.coingecko_id}`" class="nav-link main-link">
            {{ currency.name }}
          </router-link>
          <router-link :to="`/forecast/${currency.coingecko_id}`" class="nav-link forecast-link">
            [预测]
          </router-link>
        </li>
      </ul>
    </aside>
</template>

<style scoped>
.app-sidebar {
    grid-area: sidebar;
    background-color: #f8f9fa;
    padding: 20px;
    border-right: 1px solid #e0e0e0;
}

.app-sidebar h2 {
    font-size: 18px;
    color: #6c757d;
    text-transform: uppercase;
    margin-top: 0;
    margin-bottom: 20px;
}

.main-navigation {
    margin-bottom: 20px;
}

.main-nav-link {
    display: block;
    padding: 15px;
    margin-bottom: 10px;
    border-radius: 8px;
    text-decoration: none;
    color: #2c3e50;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 600;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}

.main-nav-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.nav-divider {
    border: none;
    height: 1px;
    background: #e0e0e0;
    margin: 20px 0;
}

.app-sidebar h3 {
    font-size: 14px;
    color: #6c757d;
    text-transform: uppercase;
    margin-bottom: 15px;
    font-weight: 600;
}

.loading-text {
    color: #6c757d;
}

.navigation-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.nav-link {
    display: block;
    padding: 12px 15px;
    margin-bottom: 5px;
    border-radius: 6px;
    text-decoration: none;
    /* 移除链接下划线 */
    color: #343a40;
    transition: background-color 0.2s, color 0.2s;
}

.nav-link:hover {
    background-color: #e9ecef;
}

/* Vue Router会自动为当前激活的链接添加 'router-link-active' class */
.nav-link.router-link-active {
    background-color: #007bff;
    color: white;
    font-weight: 600;
}

.nav-item-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}
.main-link {
  flex-grow: 1;
}
.forecast-link {
  font-size: 12px;
  margin-left: 10px;
  white-space: nowrap;
}
/* 修正高亮逻辑：让容器根据内部链接是否激活来判断 */
.nav-item-container:has(.router-link-active) .main-link {
  background-color: #007bff;
  color: white;
  font-weight: 600;
}
</style>