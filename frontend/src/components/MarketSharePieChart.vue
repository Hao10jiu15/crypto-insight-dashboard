<script setup>
import { ref, onMounted } from 'vue';
import { getMarketShare } from '../services/api';

// ECharts 模块导入
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart } from 'echarts/charts';
import {
    TitleComponent,
    TooltipComponent,
    LegendComponent,
} from 'echarts/components';
import VChart from 'vue-echarts';

import ChartSkeleton from './skeletons/ChartSkeleton.vue'; // 导入图表骨架屏


// 注册ECharts模块
use([
    CanvasRenderer,
    PieChart,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
]);

const isLoading = ref(true);
const error = ref(null);
const chartOption = ref({});

onMounted(async () => {
    try {
        const response = await getMarketShare();

        chartOption.value = {
            title: {
                text: 'Top 10 市值占比',
                left: 'center',
                top: '5%',
            },
            tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b} : ${c} ({d}%)' // a: series name, b: data name, c: value, d: percentage
            },
            legend: {
                orient: 'vertical',
                left: 'left',
                top: '15%',
            },
            series: [
                {
                    name: '市值',
                    type: 'pie',
                    radius: ['45%', '75%'], // 创建一个环形图（甜甜圈图）
                    center: ['60%', '55%'], // 调整饼图位置
                    avoidLabelOverlap: false,
                    label: {
                        show: false,
                        position: 'center'
                    },
                    emphasis: {
                        label: {
                            show: true,
                            fontSize: '24',
                            fontWeight: 'bold'
                        }
                    },
                    labelLine: {
                        show: false
                    },
                    data: response.data,
                }
            ]
        };

    } catch (err) {
        console.error("获取市值数据失败:", err);
        error.value = "无法加载市值占比图。";
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
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.chart {
    height: 500px;
}

.status-message {
    height: 500px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #6a737d;
}

.error {
    color: #d73a49;
}
</style>