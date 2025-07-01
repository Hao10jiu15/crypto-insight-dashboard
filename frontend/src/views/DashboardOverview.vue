<script setup>
import MarketHeatmapChart from '../components/MarketHeatmapChart.vue';
import MarketSharePieChart from '../components/MarketSharePieChart.vue';
import MarketStatsCards from '../components/MarketStatsCards.vue';
import TrendComparisonChart from '../components/TrendComparisonChart.vue';
import VolumeRankingChart from '../components/VolumeRankingChart.vue';
</script>

<template>
    <div class="overview-container">
        <h1 class="page-title">市场总览</h1>
        <p class="page-subtitle">从宏观角度洞察加密货币市场动态和趋势。</p>

        <!-- 市场统计卡片 -->
        <MarketStatsCards />

        <!-- 图表网格布局 -->
        <div class="charts-grid">
            <!-- 第一行：市场份额和趋势对比 -->
            <div class="chart-row">
                <div class="chart-wrapper half">
                    <MarketSharePieChart />
                </div>
                <div class="chart-wrapper half">
                    <TrendComparisonChart />
                </div>
            </div>

            <!-- 第二行：交易量排行和市场热度图 -->
            <div class="chart-row">
                <div class="chart-wrapper half">
                    <VolumeRankingChart />
                </div>
                <div class="chart-wrapper half">
                    <MarketHeatmapChart />
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.overview-container {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.page-title {
    font-size: 28px;
    margin-bottom: 5px;
    color: #2c3e50;
}

.page-subtitle {
    font-size: 16px;
    color: #6a737d;
    margin-bottom: 30px;
}

.charts-grid {
    display: flex;
    flex-direction: column;
    gap: 30px;
}

.chart-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.chart-wrapper {
    min-height: 400px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
    .chart-row {
        grid-template-columns: 1fr;
        gap: 20px;
    }
}

@media (max-width: 768px) {
    .overview-container {
        padding: 10px;
    }
    
    .page-title {
        font-size: 24px;
    }
    
    .page-subtitle {
        font-size: 14px;
    }
    
    .charts-grid {
        gap: 20px;
    }
}
</style>