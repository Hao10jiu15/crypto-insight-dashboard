<script setup>
import { onMounted, ref } from 'vue';
import { getCurrencyMetrics } from '../services/api';
import { useMainStore } from '../stores/mainStore';

// ECharts 模块导入
import { BarChart } from 'echarts/charts';
import {
    GridComponent,
    LegendComponent,
    TitleComponent,
    TooltipComponent
} from 'echarts/components';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import VChart from 'vue-echarts';

import ChartSkeleton from './skeletons/ChartSkeleton.vue';

// 注册ECharts模块
use([
    CanvasRenderer,
    BarChart,
    TitleComponent,
    TooltipComponent,
    GridComponent,
    LegendComponent,
]);

const mainStore = useMainStore();
const isLoading = ref(true);
const error = ref(null);
const chartOption = ref({});

const formatVolume = (volume) => {
    if (volume >= 1e9) return `$${(volume / 1e9).toFixed(2)}B`;
    if (volume >= 1e6) return `$${(volume / 1e6).toFixed(2)}M`;
    if (volume >= 1e3) return `$${(volume / 1e3).toFixed(2)}K`;
    return `$${volume.toFixed(2)}`;
};

onMounted(async () => {
    try {
        if (mainStore.currencies.length === 0) {
            await mainStore.fetchCurrencies();
        }

        // 获取前15个币种的数据
        const currencies = mainStore.currencies.slice(0, 15);
        const metricsPromises = currencies.map(currency => 
            getCurrencyMetrics(currency.coingecko_id).catch(err => null)
        );
        
        const metricsResults = await Promise.all(metricsPromises);
        
        // 处理数据并按交易量排序
        const volumeData = [];
        const priceChangeData = [];
        const currencyNames = [];
        
        metricsResults.forEach((result, index) => {
            if (result && result.data && result.data.volume_24h) {
                const currency = currencies[index];
                const data = result.data;
                
                volumeData.push({
                    name: currency.name,
                    value: data.volume_24h,
                    priceChange: data.price_change_percentage_24h || 0
                });
            }
        });
        
        // 按交易量排序
        volumeData.sort((a, b) => b.value - a.value);
        
        // 取前10名
        const top10Volume = volumeData.slice(0, 10);
        
        top10Volume.forEach(item => {
            currencyNames.push(item.name);
            priceChangeData.push(item.priceChange);
        });

        chartOption.value = {
            title: {
                text: 'Top 10 24小时交易量排行',
                left: 'center',
                top: '5%',
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                },
                formatter: function(params) {
                    const data = params[0];
                    const volume = formatVolume(data.value);
                    const change = priceChangeData[data.dataIndex];
                    const changeColor = change >= 0 ? '#00da3c' : '#ec0000';
                    const changeText = change >= 0 ? `+${change.toFixed(2)}%` : `${change.toFixed(2)}%`;
                    
                    return `${data.name}<br/>
                           交易量: ${volume}<br/>
                           <span style="color: ${changeColor}">24h变化: ${changeText}</span>`;
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                top: '15%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: {
                type: 'value',
                axisLabel: {
                    formatter: function(value) {
                        return formatVolume(value);
                    }
                }
            },
            yAxis: {
                type: 'category',
                data: currencyNames.reverse(), // 反转以使最大值在顶部
                axisLabel: {
                    interval: 0
                }
            },
            series: [
                {
                    name: '24小时交易量',
                    type: 'bar',
                    data: top10Volume.map(item => item.value).reverse(),
                    itemStyle: {
                        color: function(params) {
                            // 根据价格变化设置颜色
                            const change = priceChangeData[currencyNames.length - 1 - params.dataIndex];
                            if (change > 5) return '#00da3c';
                            if (change > 0) return '#90EE90';
                            if (change > -5) return '#FFB6C1';
                            return '#ec0000';
                        },
                        borderRadius: [0, 4, 4, 0]
                    },
                    label: {
                        show: true,
                        position: 'right',
                        formatter: function(params) {
                            return formatVolume(params.value);
                        },
                        fontSize: 12
                    },
                    animationDelay: function (idx) {
                        return idx * 100;
                    }
                }
            ],
            animationEasing: 'elasticOut',
            animationDelayUpdate: function (idx) {
                return idx * 50;
            }
        };

    } catch (err) {
        console.error("获取交易量数据失败:", err);
        error.value = "无法加载交易量排行图。";
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
