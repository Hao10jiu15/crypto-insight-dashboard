<script setup>
import { onMounted, ref } from 'vue';
import { getMarketData } from '../services/api';
import { useMainStore } from '../stores/mainStore';

// ECharts 模块导入
import { LineChart } from 'echarts/charts';
import {
    DataZoomComponent,
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
    LineChart,
    TitleComponent,
    TooltipComponent,
    GridComponent,
    LegendComponent,
    DataZoomComponent,
]);

const mainStore = useMainStore();
const isLoading = ref(true);
const error = ref(null);
const chartOption = ref({});

// 预定义颜色
const colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'];

onMounted(async () => {
    try {
        if (mainStore.currencies.length === 0) {
            await mainStore.fetchCurrencies();
        }

        // 选择主要币种进行对比
        const majorCurrencies = mainStore.currencies.slice(0, 6);
        const dataPromises = majorCurrencies.map(currency => 
            getMarketData({ currency_id: currency.coingecko_id, interval: '1d' })
                .catch(err => ({ data: null, error: err }))
        );
        
        const dataResults = await Promise.all(dataPromises);
        
        // 处理数据
        const series = [];
        
        dataResults.forEach((result, index) => {
            if (result.data && result.data.data && result.data.data.length > 0) {
                const currency = majorCurrencies[index];
                const rawData = result.data.data;
                
                // 将价格数据标准化为百分比变化
                const firstPrice = rawData[0][4]; // 使用收盘价
                const normalizedData = rawData.map(item => {
                    const timestamp = item[0];
                    const closePrice = item[4];
                    const percentChange = ((closePrice - firstPrice) / firstPrice) * 100;
                    return [timestamp, percentChange];
                });
                
                series.push({
                    name: currency.name,
                    type: 'line',
                    data: normalizedData,
                    smooth: true,
                    showSymbol: false,
                    lineStyle: {
                        width: 2,
                        color: colors[index % colors.length]
                    }
                });
            }
        });

        chartOption.value = {
            title: {
                text: '主要加密货币价格趋势对比',
                subtext: '以首日价格为基准的百分比变化',
                left: 'center',
                top: '2%',
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    animation: false
                },
                formatter: function(params) {
                    const date = new Date(params[0].value[0]).toLocaleDateString();
                    let result = `${date}<br/>`;
                    params.forEach(param => {
                        const change = param.value[1];
                        const color = change >= 0 ? '#00da3c' : '#ec0000';
                        result += `<span style="color: ${color}">${param.seriesName}: ${change >= 0 ? '+' : ''}${change.toFixed(2)}%</span><br/>`;
                    });
                    return result;
                }
            },
            legend: {
                top: '12%',
                data: series.map(s => s.name)
            },
            grid: {
                left: '3%',
                right: '4%',
                top: '22%',
                bottom: '15%',
                containLabel: true
            },
            xAxis: {
                type: 'time',
                boundaryGap: false,
                axisLabel: {
                    formatter: (value) => {
                        const date = new Date(value);
                        return `${date.getMonth() + 1}/${date.getDate()}`;
                    }
                }
            },
            yAxis: {
                type: 'value',
                scale: true,
                axisLabel: {
                    formatter: '{value}%'
                },
                splitLine: {
                    lineStyle: {
                        type: 'dashed'
                    }
                }
            },
            dataZoom: [
                {
                    type: 'inside',
                    start: 50,
                    end: 100
                },
                {
                    show: true,
                    type: 'slider',
                    top: '90%',
                    start: 50,
                    end: 100
                }
            ],
            series: series
        };

    } catch (err) {
        console.error("获取趋势对比数据失败:", err);
        error.value = "无法加载趋势对比图。";
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
