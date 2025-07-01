<script setup>
import { ref, watch } from 'vue';
import { getMarketData } from '../services/api';

// ECharts 模块导入
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { CandlestickChart, BarChart } from 'echarts/charts'; // 新增导入 BarChart
import {
    TitleComponent,
    TooltipComponent,
    GridComponent,
    DataZoomComponent,
    LegendComponent,
    AxisPointerComponent, // 新增导入 AxisPointer
} from 'echarts/components';
import VChart from 'vue-echarts';

import ChartSkeleton from './skeletons/ChartSkeleton.vue'; // 导入图表骨架屏


// 注册ECharts模块
use([
    CanvasRenderer,
    CandlestickChart,
    BarChart, // 注册 BarChart
    TitleComponent,
    TooltipComponent,
    GridComponent,
    DataZoomComponent,
    LegendComponent,
    AxisPointerComponent, // 注册 AxisPointer
]);

const props = defineProps({
    currencyId: { type: String, required: true },
    currencyName: { type: String, default: '加密货币' }
});

const isLoading = ref(true);
const error = ref(null);
const chartOption = ref({});

async function fetchAndSetChartData() {
    if (!props.currencyId) return;

    isLoading.value = true;
    error.value = null;
    try {
        const params = { currency_id: props.currencyId, interval: '1d' };
        const response = await getMarketData(params);
        const rawData = response.data.data;

        // --- 数据处理 ---
        // 将后端返回的数据拆分为 ECharts 需要的格式
        const ohlcData = rawData.map(item => [item[0], item[1], item[2], item[3], item[4]]);
        const volumeData = rawData.map(item => [item[0], item[5]]); // [时间戳, 交易量]

        // --- ECharts 配置 ---
        chartOption.value = {
            title: {
                text: `${props.currencyName} 市场数据 (USD)`,
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'cross' },
            },
            // 联动两个图表的关键
            axisPointer: {
                link: [{ xAxisIndex: 'all' }],
                label: { backgroundColor: '#777' }
            },
            // 上下排列两个图表
            grid: [
                { left: '10%', right: '8%', height: '50%' }, // K线图的grid
                { left: '10%', right: '8%', top: '65%', height: '16%' } // 交易量图的grid
            ],
            // X轴定义
            xAxis: [
                { gridIndex: 0, type: 'time', axisLabel: { show: false } }, // K线图的X轴，不显示标签
                { gridIndex: 1, type: 'time' } // 交易量图的X轴，显示标签
            ],
            // Y轴定义
            yAxis: [
                { gridIndex: 0, scale: true }, // K线图的Y轴
                { gridIndex: 1, scale: true, axisLabel: { show: false }, splitLine: { show: false } } // 交易量图的Y轴
            ],
            // 缩放控制器
            dataZoom: [
                {
                    type: 'inside',
                    xAxisIndex: [0, 1], // 同时控制两个X轴
                    start: 50,
                    end: 100,
                },
                {
                    show: true,
                    type: 'slider',
                    xAxisIndex: [0, 1], // 同时控制两个X轴
                    top: '90%',
                    start: 50,
                    end: 100,
                },
            ],
            series: [
                {
                    name: '价格 (OHLC)',
                    type: 'candlestick',
                    xAxisIndex: 0,
                    yAxisIndex: 0,
                    data: ohlcData,
                    itemStyle: { color: '#00da3c', color0: '#ec0000', borderColor: '#00da3c', borderColor0: '#ec0000' },
                },
                {
                    name: '交易量',
                    type: 'bar', // 图表类型为柱状图
                    xAxisIndex: 1,
                    yAxisIndex: 1,
                    data: volumeData,
                }
            ],
        };

    } catch (err) {
        console.error(`获取 ${props.currencyName} 市场数据失败:`, err);
        error.value = '无法加载图表数据。';
    } finally {
        isLoading.value = false;
    }
}

watch(() => props.currencyId, () => {
    fetchAndSetChartData();
}, { immediate: true });
</script>

<template>
    <div class="chart-container">
        <ChartSkeleton v-if="isLoading" />
        <div v-else-if="error" class="status-message error">{{ error }}</div>
        <v-chart v-else class="chart" :option="chartOption" autoresize />
    </div>
</template>

<style scoped>
/* 样式保持不变 */
.chart-container {
    border: 1px solid #dfe3e8;
    border-radius: 8px;
    padding: 20px;
    margin-top: 20px;
}

.chart {
    height: 600px;
    /* 增加了图表高度以容纳两个图 */
}

.status-message {
    height: 600px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #6a737d;
}

.error {
    color: #d73a49;
}
</style>