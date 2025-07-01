<script setup>
import { onMounted, ref } from 'vue';
import { getCurrencyMetrics } from '../services/api';
import { useMainStore } from '../stores/mainStore';

const mainStore = useMainStore();
const isLoading = ref(true);
const error = ref(null);
const marketStats = ref({
    totalMarketCap: 0,
    totalVolume24h: 0,
    dominance: {},
    gainersCount: 0,
    losersCount: 0,
    avgChange24h: 0
});

const formatNumber = (num) => {
    if (num === null || num === undefined) return 'N/A';
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toLocaleString();
};

const formatCurrency = (num) => {
    if (num === null || num === undefined) return 'N/A';
    return `$${formatNumber(num)}`;
};

onMounted(async () => {
    try {
        if (mainStore.currencies.length === 0) {
            await mainStore.fetchCurrencies();
        }

        // 获取前20个币种的数据进行统计
        const currencies = mainStore.currencies.slice(0, 20);
        const metricsPromises = currencies.map(currency => 
            getCurrencyMetrics(currency.coingecko_id).catch(err => null)
        );
        
        const metricsResults = await Promise.all(metricsPromises);
        
        // 计算市场统计数据
        let totalMarketCap = 0;
        let totalVolume24h = 0;
        let priceChanges = [];
        let gainers = 0;
        let losers = 0;
        
        metricsResults.forEach((result, index) => {
            if (result && result.data) {
                const data = result.data;
                const currency = currencies[index];
                
                if (data.market_cap) totalMarketCap += data.market_cap;
                if (data.volume_24h) totalVolume24h += data.volume_24h;
                
                if (data.price_change_percentage_24h !== null) {
                    const change = data.price_change_percentage_24h;
                    priceChanges.push(change);
                    
                    if (change > 0) gainers++;
                    else if (change < 0) losers++;
                }
            }
        });
        
        const avgChange = priceChanges.length > 0 
            ? priceChanges.reduce((sum, change) => sum + change, 0) / priceChanges.length 
            : 0;
        
        // 计算比特币和以太坊的市场占有率
        const btcData = metricsResults.find((result, index) => 
            currencies[index].coingecko_id === 'bitcoin' && result?.data
        );
        const ethData = metricsResults.find((result, index) => 
            currencies[index].coingecko_id === 'ethereum' && result?.data
        );
        
        const btcDominance = btcData && totalMarketCap > 0 
            ? (btcData.data.market_cap / totalMarketCap * 100).toFixed(1) 
            : 0;
        const ethDominance = ethData && totalMarketCap > 0 
            ? (ethData.data.market_cap / totalMarketCap * 100).toFixed(1) 
            : 0;

        marketStats.value = {
            totalMarketCap,
            totalVolume24h,
            dominance: {
                bitcoin: btcDominance,
                ethereum: ethDominance
            },
            gainersCount: gainers,
            losersCount: losers,
            avgChange24h: avgChange
        };

    } catch (err) {
        console.error("获取市场统计数据失败:", err);
        error.value = "无法加载市场统计数据。";
    } finally {
        isLoading.value = false;
    }
});
</script>

<template>
    <div class="market-stats-container">
        <h2 class="section-title">市场概况</h2>
        
        <div v-if="isLoading" class="loading-skeleton">
            <div class="skeleton-card" v-for="i in 6" :key="i"></div>
        </div>
        
        <div v-else-if="error" class="error-message">{{ error }}</div>
        
        <div v-else class="stats-grid">
            <div class="stat-card primary">
                <div class="stat-icon">📊</div>
                <div class="stat-content">
                    <span class="label">总市值</span>
                    <span class="value">{{ formatCurrency(marketStats.totalMarketCap) }}</span>
                </div>
            </div>
            
            <div class="stat-card secondary">
                <div class="stat-icon">💰</div>
                <div class="stat-content">
                    <span class="label">24小时交易量</span>
                    <span class="value">{{ formatCurrency(marketStats.totalVolume24h) }}</span>
                </div>
            </div>
            
            <div class="stat-card success">
                <div class="stat-icon">📈</div>
                <div class="stat-content">
                    <span class="label">上涨币种</span>
                    <span class="value">{{ marketStats.gainersCount }}</span>
                </div>
            </div>
            
            <div class="stat-card danger">
                <div class="stat-icon">📉</div>
                <div class="stat-content">
                    <span class="label">下跌币种</span>
                    <span class="value">{{ marketStats.losersCount }}</span>
                </div>
            </div>
            
            <div class="stat-card info">
                <div class="stat-icon">₿</div>
                <div class="stat-content">
                    <span class="label">BTC市场占有率</span>
                    <span class="value">{{ marketStats.dominance.bitcoin }}%</span>
                </div>
            </div>
            
            <div class="stat-card warning">
                <div class="stat-icon">Ξ</div>
                <div class="stat-content">
                    <span class="label">ETH市场占有率</span>
                    <span class="value">{{ marketStats.dominance.ethereum }}%</span>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.market-stats-container {
    margin-bottom: 30px;
}

.section-title {
    font-size: 22px;
    margin-bottom: 20px;
    color: #2c3e50;
    padding-bottom: 10px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
}

.stat-card {
    background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    display: flex;
    align-items: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border-left: 4px solid transparent;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.stat-card.primary { border-left-color: #007bff; }
.stat-card.secondary { border-left-color: #6c757d; }
.stat-card.success { border-left-color: #28a745; }
.stat-card.danger { border-left-color: #dc3545; }
.stat-card.info { border-left-color: #17a2b8; }
.stat-card.warning { border-left-color: #ffc107; }

.stat-icon {
    font-size: 32px;
    margin-right: 15px;
    opacity: 0.8;
}

.stat-content {
    display: flex;
    flex-direction: column;
}

.label {
    font-size: 14px;
    color: #6a737d;
    margin-bottom: 4px;
    font-weight: 500;
}

.value {
    font-size: 24px;
    font-weight: 700;
    color: #2c3e50;
}

.loading-skeleton {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
}

.skeleton-card {
    height: 80px;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
    border-radius: 12px;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

.error-message {
    text-align: center;
    padding: 40px;
    color: #dc3545;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 8px;
}
</style>
