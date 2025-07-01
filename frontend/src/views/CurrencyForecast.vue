<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import ComponentChart from '../components/ComponentChart.vue';
import ForecastChart from '../components/ForecastChart.vue';
import PredictionAccuracyChart from '../components/PredictionAccuracyChart.vue';
import { getCompleteForecastData, getForecastComponents, getForecastData, getMarketData } from '../services/api';
import { useMainStore } from '../stores/mainStore';

const props = defineProps({
  id: { type: String, required: true }
});

const mainStore = useMainStore();
const forecastData = ref([]);
const completeForecastData = ref([]); // 完整预测数据
const actualData = ref([]);
const componentData = ref(null);
const isLoading = ref(true);
const error = ref(null);  // 新增错误状态

const currencyName = computed(() => mainStore.currencies.find(c => c.coingecko_id === props.id)?.name || '...');

async function fetchData(currencyId) {
  if (!currencyId) return;
  isLoading.value = true;
  error.value = null;  // 重置错误状态
  
  // 重置所有数据状态，防止显示上一个货币的数据
  forecastData.value = [];
  completeForecastData.value = [];
  actualData.value = [];
  componentData.value = null;
  
  try {
    // 并行获取所有需要的数据
    const [forecastRes, completeForecastRes, marketRes, componentsRes] = await Promise.all([
      getForecastData({ currency_id: currencyId }).catch(err => ({ data: null, error: err })),
      getCompleteForecastData({ currency_id: currencyId }).catch(err => ({ data: null, error: err })),
      getMarketData({ currency_id: currencyId }).catch(err => ({ data: null, error: err })),
      getForecastComponents({ currency_id: currencyId }).catch(err => ({ data: null, error: err }))
    ]);
    
    // 检查预测数据
    if (forecastRes.error || !forecastRes.data || forecastRes.data.length === 0) {
      if (forecastRes.error?.response?.status === 404) {
        error.value = `${currencyName.value} 暂无预测模型。此货币可能是稳定币或数据不足以进行预测。`;
      } else {
        error.value = "未找到预测数据";
      }
      forecastData.value = [];
    } else {
      forecastData.value = forecastRes.data;
    }
    
    // 检查完整预测数据
    if (completeForecastRes.error || !completeForecastRes.data || completeForecastRes.data.length === 0) {
      console.warn("完整预测数据缺失");
      completeForecastData.value = [];
    } else {
      completeForecastData.value = completeForecastRes.data;
    }
    
    // 检查市场数据
    if (marketRes.error || !marketRes.data || !marketRes.data.data || marketRes.data.data.length === 0) {
      console.warn("市场数据缺失");
      actualData.value = [];
    } else {
      actualData.value = marketRes.data.data;
    }
    
    // 检查组件数据
    if (componentsRes.error || !componentsRes.data) {
      componentData.value = null;
    } else {
      componentData.value = componentsRes.data;
    }
    
  } catch (err) {
    console.error("获取预测相关数据失败:", err);
    error.value = `获取预测数据失败: ${err.message || '未知错误'}`;
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  if (mainStore.currencies.length === 0) mainStore.fetchCurrencies();
});

watch(() => props.id, (newId) => {
  if (newId) fetchData(newId);
}, { immediate: true });
</script>

<template>
  <div class="forecast-page">
    <div class="page-header">
      <h1 class="page-title">{{ currencyName }} 价格预测</h1>
      <p class="page-subtitle">基于Prophet模型的未来3天价格走势预测。</p>
    </div>

    <div v-if="isLoading" class="status-message loading">
      <div class="spinner"></div>
      <p>正在加载预测数据...</p>
    </div>
    
    <div v-else-if="error" class="status-message error">
      <p>{{ error }}</p>
      <button @click="fetchData(props.id)" class="retry-button">重试</button>
    </div>
    
    <div v-else class="content-container">
      <div class="chart-section">
        <ForecastChart 
          v-if="forecastData.length && actualData.length" 
          :forecast-data="forecastData" 
          :actual-data="actualData"
          :complete-forecast-data="completeForecastData"
        />
        <div v-else-if="forecastData.length && !actualData.length" class="warning-message">
          <ForecastChart 
            :forecast-data="forecastData" 
            :actual-data="[]"
            :complete-forecast-data="completeForecastData"
          />
          <p>注意：历史价格数据不可用，仅显示预测数据</p>
        </div>
        <div v-else class="status-message">暂无此货币的预测数据。</div>
      </div>

      <div v-if="componentData" class="components-section">
        <h2 class="section-title">模型洞察分析</h2>
        <div class="components-grid">
          <ComponentChart 
            v-for="(data, name) in componentData"
            :key="name"
            :title="name"
            :data="data"
          />
        </div>
      </div>

      <!-- 预测准确性分析 -->
      <div v-if="completeForecastData.length && actualData.length" class="accuracy-section">
        <PredictionAccuracyChart 
          :forecast-data="completeForecastData"
          :actual-data="actualData"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.forecast-page {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 30px;
}

.content-container {
  width: 100%;
  max-width: 100%;
}

.chart-section {
  width: 100%;
  margin-bottom: 40px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #007bff;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-button {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-button:hover {
  background-color: #0069d9;
}

.warning-message {
  position: relative;
}

.warning-message p {
  background-color: #fff3cd;
  color: #856404;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
  text-align: center;
}

.page-title { 
  font-size: 28px; 
  margin-bottom: 5px; 
  color: #333;
}

.page-subtitle { 
  font-size: 16px; 
  color: #6a737d; 
  margin-bottom: 0;
}

.status-message { 
  text-align: center; 
  padding: 50px; 
  color: #6a737d; 
}

.error { 
  color: #dc3545; 
}

.components-section { 
  margin-top: 40px; 
  width: 100%;
}

.accuracy-section {
  margin-top: 40px;
  width: 100%;
}

.section-title { 
  font-size: 22px; 
  border-bottom: 2px solid #007bff; 
  padding-bottom: 10px; 
  margin-bottom: 20px; 
}

.components-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  width: 100%;
}

/* 响应式设计：在小屏幕上改为单列 */
@media (max-width: 1200px) {
  .components-grid {
    grid-template-columns: 1fr;
  }
}
</style>