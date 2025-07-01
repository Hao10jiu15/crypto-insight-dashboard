<script setup>
import { LineChart } from 'echarts/charts';
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { computed } from 'vue';
import VChart from 'vue-echarts';

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent]);

const props = defineProps({
  forecastData: { type: Array, required: true },
  actualData: { type: Array, required: true },
  completeForecastData: { type: Array, default: () => [] }, // 完整预测数据（历史+未来）
});

const chartOption = computed(() => {
  // 调试信息：检查传入的数据
  console.log('🔍 ForecastChart DEBUG:');
  console.log('forecastData length:', props.forecastData.length);
  console.log('actualData length:', props.actualData.length);
  console.log('completeForecastData length:', props.completeForecastData.length);
  
  if (props.forecastData.length > 0) {
    console.log('forecastData sample:', props.forecastData[0]);
  }
  if (props.completeForecastData.length > 0) {
    console.log('completeForecastData sample:', props.completeForecastData[0]);
  }

  // 修复日期处理逻辑，统一使用时间戳
  const timestamps = props.forecastData.map(p => new Date(p.time).getTime());
  const dates = timestamps.map(ts => new Date(ts).toLocaleDateString());
  
  // 确保实际价格数据按时间排序
  const sortedActuals = [...props.actualData]
    .sort((a, b) => a[0] - b[0])
    .map(d => [d[0], d[4]]); // [timestamp, close]
  
  // 提取预测价格和置信区间
  const predictions = props.forecastData.map(p => p.predicted_price);
  
  // 确保置信区间数据格式正确
  const confidenceBand = props.forecastData.map((p, index) => [
    timestamps[index], // 使用时间戳而不是格式化后的日期字符串
    p.prediction_lower_bound,
    p.prediction_upper_bound
  ]);

  // 处理完整预测数据（历史拟合+未来预测）
  const completePredictionLine = props.completeForecastData.length > 0 
    ? props.completeForecastData.map(p => [new Date(p.time).getTime(), p.predicted_price])
    : [];

  // 构建系列数据
  const series = [
    {
      name: '实际价格',
      type: 'line',
      data: sortedActuals,
      showSymbol: false,
      lineStyle: { color: '#1f77b4', width: 2 }
    }
  ];

  // 如果有完整预测数据，显示完整预测曲线
  if (completePredictionLine.length > 0) {
    console.log('添加完整预测曲线，数据点数:', completePredictionLine.length);
    console.log('完整预测曲线样本:', completePredictionLine.slice(0, 3));
    series.push({
      name: '完整预测曲线',
      type: 'line',
      data: completePredictionLine,
      showSymbol: false,
      lineStyle: { 
        type: 'solid', 
        color: '#ff7f0e', 
        width: 2,
        opacity: 0.8 
      }
    });
  } else {
    console.log('❌ 没有完整预测数据');
  }

  // 添加未来预测数据（虚线显示）
  if (props.forecastData.length > 0) {
    const futureData = props.forecastData.map(p => [new Date(p.time).getTime(), p.predicted_price]);
    console.log('添加未来预测，数据点数:', futureData.length);
    console.log('未来预测样本:', futureData.slice(0, 3));
    series.push({
      name: '未来预测',
      type: 'line',
      data: futureData,
      showSymbol: false,
      lineStyle: { 
        type: 'dashed', 
        color: '#d62728', 
        width: 2 
      }
    });
  } else {
    console.log('❌ 没有未来预测数据');
  }

  // 添加置信区间
  if (confidenceBand.length > 0) {
    series.push(
      {
        name: '置信区间',
        type: 'line',
        data: confidenceBand.map(item => [item[0], item[1]]),
        lineStyle: { opacity: 0 },
        stack: 'confidence-band',
        symbol: 'none'
      },
      {
        name: '置信区间',
        type: 'line',
        data: confidenceBand.map(item => [item[0], item[2]]),
        lineStyle: { opacity: 0 },
        areaStyle: { color: 'rgba(0,0,0,0.1)' },
        stack: 'confidence-band',
        symbol: 'none'
      }
    );
  }

  return {
    tooltip: { 
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        animation: false
      },
      formatter: function(params) {
        const timestamp = params[0].value[0];
        const date = new Date(timestamp).toLocaleDateString();
        let result = `<strong>${date}</strong><br/>`;
        
        console.log('🔍 Tooltip DEBUG:', {
          timestamp,
          date,
          paramsLength: params.length,
          paramsSeries: params.map(p => p.seriesName)
        });
        
        // 查找最接近的实际价格
        let actualPrice = null;
        const actualParam = params.find(p => p.seriesName === '实际价格');
        if (actualParam && actualParam.value[1] !== null) {
          actualPrice = actualParam.value[1];
        }
        
        // 查找最接近的完整预测价格
        let completeForecastPrice = null;
        let completeForecastTimeDiff = Infinity;
        if (props.completeForecastData.length > 0) {
          const targetTime = timestamp;
          let closestIndex = 0;
          let minDiff = Math.abs(new Date(props.completeForecastData[0].time).getTime() - targetTime);
          
          for (let i = 1; i < props.completeForecastData.length; i++) {
            const diff = Math.abs(new Date(props.completeForecastData[i].time).getTime() - targetTime);
            if (diff < minDiff) {
              minDiff = diff;
              closestIndex = i;
            }
          }
          
          completeForecastTimeDiff = minDiff;
          // 如果时间差在3天以内，使用这个预测值
          if (minDiff <= 3 * 24 * 60 * 60 * 1000) {
            completeForecastPrice = parseFloat(props.completeForecastData[closestIndex].predicted_price);
          }
        }
        
        // 查找最接近的未来预测价格
        let futurePrice = null;
        let futureTimeDiff = Infinity;
        if (props.forecastData.length > 0) {
          const targetTime = timestamp;
          let closestIndex = 0;
          let minDiff = Math.abs(new Date(props.forecastData[0].time).getTime() - targetTime);
          
          for (let i = 1; i < props.forecastData.length; i++) {
            const diff = Math.abs(new Date(props.forecastData[i].time).getTime() - targetTime);
            if (diff < minDiff) {
              minDiff = diff;
              closestIndex = i;
            }
          }
          
          futureTimeDiff = minDiff;
          // 如果时间差在3天以内，使用这个预测值
          if (minDiff <= 3 * 24 * 60 * 60 * 1000) {
            futurePrice = parseFloat(props.forecastData[closestIndex].predicted_price);
          }
        }
        
        // 智能显示逻辑：避免同时显示三种价格
        let hasAnyData = false;
        
        // 1. 如果有实际价格，优先显示实际价格
        if (actualPrice !== null) {
          result += `<span style="color: #1f77b4; font-weight: 500;">● 实际价格: $${actualPrice.toFixed(2)}</span><br/>`;
          hasAnyData = true;
          
          // 如果实际价格存在，总是显示历史拟合（如果有的话），方便对比模型拟合效果
          if (completeForecastPrice !== null) {
            result += `<span style="color: #ff7f0e; font-weight: 500;">▲ 历史拟合: $${completeForecastPrice.toFixed(2)}</span><br/>`;
          }
        } 
        // 2. 如果没有实际价格，判断是历史拟合区域还是未来预测区域
        else {
          // 获取当前时间戳，用于判断是否为未来时间
          const currentTime = new Date().getTime();
          const isHistorical = timestamp < currentTime;
          
          if (isHistorical && completeForecastPrice !== null) {
            // 历史区域：显示历史拟合价格
            result += `<span style="color: #ff7f0e; font-weight: 500;">▲ 历史拟合: $${completeForecastPrice.toFixed(2)}</span><br/>`;
            hasAnyData = true;
          } else if (!isHistorical && futurePrice !== null) {
            // 未来区域：显示未来预测价格
            result += `<span style="color: #d62728; font-weight: 500;">◆ 未来预测: $${futurePrice.toFixed(2)}</span><br/>`;
            hasAnyData = true;
          } else if (completeForecastPrice !== null) {
            // 如果只有完整预测数据，显示它
            result += `<span style="color: #ff7f0e; font-weight: 500;">▲ 预测价格: $${completeForecastPrice.toFixed(2)}</span><br/>`;
            hasAnyData = true;
          } else if (futurePrice !== null) {
            // 如果只有未来预测数据，显示它
            result += `<span style="color: #d62728; font-weight: 500;">◆ 未来预测: $${futurePrice.toFixed(2)}</span><br/>`;
            hasAnyData = true;
          }
        }
        
        // 如果没有找到任何价格数据，尝试显示最接近的数据（不考虑时间限制）
        if (!hasAnyData) {
          console.log('🔍 未找到任何匹配的价格数据，尝试显示最接近的数据');
          
          // 选择时间差最小的预测数据
          if (completeForecastTimeDiff < futureTimeDiff && props.completeForecastData.length > 0) {
            const targetTime = timestamp;
            let closestIndex = 0;
            let minDiff = Math.abs(new Date(props.completeForecastData[0].time).getTime() - targetTime);
            
            for (let i = 1; i < props.completeForecastData.length; i++) {
              const diff = Math.abs(new Date(props.completeForecastData[i].time).getTime() - targetTime);
              if (diff < minDiff) {
                minDiff = diff;
                closestIndex = i;
              }
            }
            
            const closestPrice = parseFloat(props.completeForecastData[closestIndex].predicted_price);
            const daysDiff = minDiff / (24 * 60 * 60 * 1000);
            result += `<span style="color: #ff7f0e; font-weight: 500;">▲ 预测价格: $${closestPrice.toFixed(2)}</span><br/>`;
            result += `<span style="color: #999; font-size: 11px;">（时间差: ${daysDiff.toFixed(1)}天）</span><br/>`;
            hasAnyData = true;
          } else if (props.forecastData.length > 0) {
            const targetTime = timestamp;
            let closestIndex = 0;
            let minDiff = Math.abs(new Date(props.forecastData[0].time).getTime() - targetTime);
            
            for (let i = 1; i < props.forecastData.length; i++) {
              const diff = Math.abs(new Date(props.forecastData[i].time).getTime() - targetTime);
              if (diff < minDiff) {
                minDiff = diff;
                closestIndex = i;
              }
            }
            
            const closestPrice = parseFloat(props.forecastData[closestIndex].predicted_price);
            const daysDiff = minDiff / (24 * 60 * 60 * 1000);
            result += `<span style="color: #d62728; font-weight: 500;">◆ 预测价格: $${closestPrice.toFixed(2)}</span><br/>`;
            result += `<span style="color: #999; font-size: 11px;">（时间差: ${daysDiff.toFixed(1)}天）</span><br/>`;
            hasAnyData = true;
          }
        }
        
        if (!hasAnyData) {
          result += '<span style="color: #999;">暂无价格数据</span><br/>';
        }
        
        // 显示置信区间
        const confidenceParams = params.filter(p => p.seriesName === '置信区间');
        if (confidenceParams.length >= 2) {
          const lowerBound = confidenceParams[0].value[1];
          const upperBound = confidenceParams[1].value[1];
          if (typeof lowerBound === 'number' && typeof upperBound === 'number') {
            result += `<span style="color: #888; font-size: 11px;">📊 置信区间: $${lowerBound.toFixed(2)} - $${upperBound.toFixed(2)}</span>`;
          }
        }
        
        return result;
      }
    },
    legend: { 
      data: completePredictionLine.length > 0 
        ? ['实际价格', '完整预测曲线', '未来预测', '置信区间'] 
        : ['实际价格', '未来预测', '置信区间']
    },
    xAxis: {
      type: 'time',
      axisLabel: {
        formatter: (value) => {
          const date = new Date(value);
          return `${date.getMonth() + 1}/${date.getDate()}`;
        }
      }
    },
    yAxis: { type: 'value', scale: true },
    series: series,
  };
});
</script>

<template>
  <div class="chart-container">
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>
<style scoped>
.chart-container { 
  border: 1px solid #e0e0e0; 
  border-radius: 8px; 
  padding: 20px; 
  background-color: #fff; 
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden; /* 防止图表溢出 */
}
.chart { 
  height: 500px; 
  width: 100%;
  max-width: 100%;
}
</style>