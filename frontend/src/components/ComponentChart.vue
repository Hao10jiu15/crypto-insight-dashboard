<script setup>
import { LineChart } from 'echarts/charts';
import { GridComponent, LegendComponent, TitleComponent, TooltipComponent } from 'echarts/components';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { computed } from 'vue';
import VChart from 'vue-echarts';

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent]);

const props = defineProps({
  title: { type: String, required: true },
  data: { type: Object, required: true },
});

const chartOption = computed(() => {
  // 数据检查与安全处理
  const hasValidData = props.data && 
    props.data.dates && 
    props.data.values && 
    props.data.lower_bound && 
    props.data.upper_bound;
  
  if (!hasValidData) {
    console.error("组件图表数据格式错误", props.data);
    // 返回一个空配置，前端会显示错误信息
    return { title: { text: `${props.title} - 数据格式错误` } };
  }
  
  const { dates, values, lower_bound, upper_bound } = props.data;
  
  return {
    title: {
      text: props.title,
      left: 'center'
    },
    tooltip: { trigger: 'axis' },
    xAxis: { 
      type: 'category', 
      data: dates,
      axisLabel: {
        rotate: dates.length > 20 ? 45 : 0,  // 日期太多时旋转标签
        interval: dates.length > 30 ? 'auto' : 0  // 控制标签显示密度
      }
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '值',
        type: 'line',
        data: values,
        z: 3  // 确保线条显示在最上层
      },
      // 使用堆叠的线图和透明的areaStyle来模拟置信区间
      {
        name: '置信下界',
        type: 'line',
        data: lower_bound,
        lineStyle: { opacity: 0 },
        stack: 'confidence-band',
        symbol: 'none'
      },
      {
        name: '置信上界',
        type: 'line',
        data: upper_bound,
        lineStyle: { opacity: 0 },
        areaStyle: { 
          color: 'rgba(0,0,0,0.1)',
          opacity: 0.5  // 调整透明度使置信区间更明显
        },
        stack: 'confidence-band',
        symbol: 'none'
      }
    ]
  };
});
</script>

<template>
  <div class="component-chart-container">
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<style scoped>
.component-chart-container {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 15px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}
.chart {
  height: 350px;
  width: 100%;
  max-width: 100%;
}
</style>