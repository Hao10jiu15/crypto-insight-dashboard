<script setup>
const props = defineProps({
    metrics: {
        type: Object,
        required: true,
    }
});

// 一个帮助函数，用于格式化数字和大额货币值
const formatNumber = (num) => {
    if (num === null || num === undefined) return 'N/A';
    return num.toLocaleString('en-US');
};

const formatCurrency = (num) => {
    if (num === null || num === undefined) return 'N/A';
    return `$${num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};
</script>

<template>
    <div class="metrics-grid">
        <div class="metric-card">
            <span class="label">当前价格</span>
            <span class="value">{{ formatCurrency(metrics.current_price) }}</span>
        </div>
        <div class="metric-card">
            <span class="label">24小时最高价</span>
            <span class="value">{{ formatCurrency(metrics.high_24h) }}</span>
        </div>
        <div class="metric-card">
            <span class="label">24小时最低价</span>
            <span class="value">{{ formatCurrency(metrics.low_24h) }}</span>
        </div>
        <div class="metric-card">
            <span class="label">24小时涨跌幅</span>
            <span class="value" :class="{
                'positive': metrics.price_change_percentage_24h > 0,
                'negative': metrics.price_change_percentage_24h < 0,
            }">
                {{ metrics.price_change_percentage_24h?.toFixed(2) }}%
            </span>
        </div>
        <div class="metric-card">
            <span class="label">总市值</span>
            <span class="value">{{ formatCurrency(metrics.market_cap) }}</span>
        </div>
    </div>
</template>

<style scoped>
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.metric-card {
    background-color: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
}

.label {
    font-size: 14px;
    color: #6a737d;
    margin-bottom: 8px;
}

.value {
    font-size: 24px;
    font-weight: 600;
    color: #2c3e50;
}

.positive {
    color: #00da3c;
}

.negative {
    color: #ec0000;
}
</style>