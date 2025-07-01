<script setup>
import { onMounted, ref } from 'vue';
import { getCurrencyMetrics } from '../services/api';
import { useMainStore } from '../stores/mainStore';

// ECharts 模块导入
import { HeatmapChart } from 'echarts/charts';
import {
    GridComponent,
    TitleComponent,
    TooltipComponent,
    VisualMapComponent
} from 'echarts/components';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import VChart from 'vue-echarts';

import ChartSkeleton from './skeletons/ChartSkeleton.vue';

// 注册ECharts模块
use([
    CanvasRenderer,
    HeatmapChart,
    TitleComponent,
    TooltipComponent,
    GridComponent,
    VisualMapComponent,
]);

const mainStore = useMainStore();
const isLoading = ref(true);
const error = ref(null);
const chartOption = ref({});

onMounted(async () => {
    try {
        if (mainStore.currencies.length === 0) {
            await mainStore.fetchCurrencies();
        }

        // 获取主要币种的指标数据
        const majorCurrencies = mainStore.currencies.slice(0, 12); // 取前12个币种
        const metricsPromises = majorCurrencies.map(currency => 
            getCurrencyMetrics(currency.coingecko_id).catch(err => null)
        );
        
        const metricsResults = await Promise.all(metricsPromises);
        
        // 处理数据构建热度图
        const heatmapData = [];
        const currencies = [];
        const metrics = ['price_change_24h', 'volume_24h', 'market_cap'];
        const metricNames = ['24h价格变化', '24h交易量', '市值'];
        
        metricsResults.forEach((result, index) => {
            if (result && result.data) {
                const currency = majorCurrencies[index];
                currencies.push(currency.name);
                
                const data = result.data;
                // 价格变化百分比
                heatmapData.push([index, 0, data.price_change_percentage_24h || 0]);
                // 交易量（对数化处理）
                const volumeScore = data.volume_24h ? Math.log10(data.volume_24h) : 0;
                heatmapData.push([index, 1, volumeScore]);
                // 市值（对数化处理）
                const marketCapScore = data.market_cap ? Math.log10(data.market_cap) : 0;
                heatmapData.push([index, 2, marketCapScore]);
            }
        });

        chartOption.value = {
            title: {
                text: '加密货币市场热度图',
                left: 'center',
                top: '5%',
            },
            tooltip: {
                position: 'top',
                formatter: function(params) {
                    const currencyName = currencies[params.data[0]];
                    const metricName = metricNames[params.data[1]];
                    let value = params.data[2];
                    
                    if (params.data[1] === 0) {
                        // 价格变化百分比
                        return `${currencyName}<br/>${metricName}: ${value.toFixed(2)}%`;
                    } else {
                        // 交易量和市值显示原始数值
                        const originalValue = Math.pow(10, value);
                        return `${currencyName}<br/>${metricName}: $${originalValue.toLocaleString()}`;
                    }
                }
            },
            grid: {
                left: '12%',
                right: '10%',
                top: '20%',
                bottom: '20%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: currencies,
                splitArea: { show: true },
                axisLabel: {
                    interval: 0,
                    rotate: 45
                }
            },
            yAxis: {
                type: 'category',
                data: metricNames,
                splitArea: { show: true }
            },
            visualMap: {
                min: -50,
                max: 50,
                calculable: true,
                orient: 'horizontal',
                left: 'center',
                bottom: '5%',
                inRange: {
                    color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', 
                           '#ffffcc', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
                }
            },
            series: [{
                name: '市场热度',
                type: 'heatmap',
                data: heatmapData,
                label: {
                    show: true,
                    formatter: function(params) {
                        if (params.data[1] === 0) {
                            return params.data[2].toFixed(1) + '%';
                        }
                        return '';
                    }
                },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        };

    } catch (err) {
        console.error("获取市场热度数据失败:", err);
        error.value = "无法加载市场热度图。";
    } finally {
        isLoading.value = false;
    }
});
</script>

<template>
    <div class="chart-container">
        <ChartSkeleton v-if="isLoading" />
        <div v-else-if="error" class="status-message error">{{ error }}</div>
        <v-chart v-else class="chart" :option="chartOption" autoresize />
    </div>
</template>

<style scoped>
.chart-container {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    background-color: #fff;
    margin-bottom: 20px;
}

.chart {
    height: 500px;
}

.status-message {
    text-align: center;
    padding: 50px;
    color: #6a737d;
}

.error {
    color: #dc3545;
}
</style>
