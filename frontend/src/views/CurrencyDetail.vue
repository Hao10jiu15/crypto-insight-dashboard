<script setup>
import { ref, watch, computed } from 'vue';
import { useMainStore } from '../stores/mainStore';
import { getCurrencyMetrics } from '../services/api';
import MetricCards from '../components/MetricCards.vue';
import PriceChart from '../components/PriceChart.vue';
import MetricCardSkeleton from '../components/skeletons/MetricCardSkeleton.vue'; // 导入指标骨架屏


const props = defineProps({
    id: { type: String, required: true } // 接收来自路由的 currency coingecko_id
});

const mainStore = useMainStore();
const currentMetrics = ref(null);
const metricsLoading = ref(false);

const currencyName = computed(() => {
    const found = mainStore.currencies.find(c => c.coingecko_id === props.id);
    return found ? found.name : '...';
});

async function fetchMetrics(currencyId) {
    if (!currencyId) return;
    metricsLoading.value = true;
    try {
        const response = await getCurrencyMetrics(currencyId);
        currentMetrics.value = response.data;
    } catch (error) {
        console.error("获取指标数据失败:", error);
    } finally {
        metricsLoading.value = false;
    }
}

watch(() => props.id, (newId) => {
    if (newId) {
        fetchMetrics(newId);
    }
}, { immediate: true });
</script>
<template>
    <div>
        <h1 class="currency-title">{{ currencyName }} 详细数据</h1>

        <MetricCardSkeleton v-if="metricsLoading" />
        <MetricCards v-else-if="currentMetrics" :metrics="currentMetrics" />
        <div v-else class="status-message error">无法加载指标数据。</div>

        <PriceChart :key="props.id" :currencyId="props.id" :currencyName="currencyName" />
    </div>
</template>
<style scoped>
.currency-title {
    font-size: 28px;
    margin-bottom: 20px;
}

.status-message {
    text-align: center;
    padding: 50px;
    color: #6a737d;
}
</style>