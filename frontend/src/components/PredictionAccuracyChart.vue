<template>
  <div class="accuracy-analysis-container">
    <div class="chart-header">
      <h3 class="chart-title">🎯 预测准确性分析</h3>
      <p class="chart-subtitle">评估模型预测与实际价格的偏差程度</p>
    </div>
    
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>正在计算预测准确性...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>
    
    <div v-else class="accuracy-content">
      <!-- 准确性指标卡片 -->
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-icon">📏</div>
          <div class="metric-info">
            <span class="metric-label">平均绝对误差</span>
            <span class="metric-value">${{ mae.toFixed(2) }}</span>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-icon">📊</div>
          <div class="metric-info">
            <span class="metric-label">均方根误差</span>
            <span class="metric-value">${{ rmse.toFixed(2) }}</span>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-icon">🎯</div>
          <div class="metric-info">
            <span class="metric-label">准确率</span>
            <span class="metric-value">{{ (accuracy * 100).toFixed(1) }}%</span>
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-icon">📈</div>
          <div class="metric-info">
            <span class="metric-label">趋势准确率</span>
            <span class="metric-value">{{ (trendAccuracy * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
      
      <!-- 预测vs实际价格图表 -->
      <div class="chart-container">
        <div ref="chartRef" class="chart"></div>
      </div>
      
      <!-- 误差分布 -->
      <div class="error-distribution">
        <h4>误差分布</h4>
        <div ref="errorChartRef" class="error-chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import * as echarts from 'echarts';
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue';

const props = defineProps({
  forecastData: {
    type: Array,
    default: () => []
  },
  actualData: {
    type: Array,
    default: () => []
  }
});

const chartRef = ref(null);
const errorChartRef = ref(null);
const isLoading = ref(true);
const error = ref(null);

// 准确性指标
const mae = ref(0);
const rmse = ref(0);
const accuracy = ref(0);
const trendAccuracy = ref(0);

let chartInstance = null;
let errorChartInstance = null;

// 计算预测准确性指标
function calculateAccuracyMetrics() {
  if (!props.forecastData.length || !props.actualData.length) {
    error.value = '数据不足，无法计算准确性指标';
    return;
  }

  try {
    console.log('开始计算准确性指标...');
    console.log('预测数据样本:', props.forecastData.slice(0, 3));
    console.log('实际数据样本:', props.actualData.slice(0, 3));

    // 创建实际数据的时间索引映射
    const actualMap = new Map();
    props.actualData.forEach(item => {
      const timestamp = item[0];
      const date = new Date(timestamp);
      // 使用YYYY-MM-DD格式作为key，更精确匹配
      const dateKey = date.toISOString().split('T')[0];
      const price = parseFloat(item[4]); // close price
      if (!isNaN(price) && price > 0) {
        actualMap.set(dateKey, price);
      }
    });

    console.log('实际数据映射条数:', actualMap.size);
    console.log('实际数据映射样本:', Array.from(actualMap.entries()).slice(0, 5));

    // 过滤出历史预测数据（不是未来预测）
    const now = new Date();
    const currentDateKey = now.toISOString().split('T')[0];
    
    const matches = [];
    props.forecastData.forEach(forecast => {
      const forecastDate = new Date(forecast.time);
      const dateKey = forecastDate.toISOString().split('T')[0];
      
      // 只使用历史数据进行准确性分析（预测时间早于当前时间）
      // 并且要确保这是历史拟合数据，而不是未来预测
      if (dateKey <= currentDateKey) {
        const predictedPrice = parseFloat(forecast.predicted_price);
        const actualPrice = actualMap.get(dateKey);
        
        if (actualPrice !== undefined && !isNaN(predictedPrice) && actualPrice > 0 && predictedPrice > 0) {
          const errorAbs = Math.abs(predictedPrice - actualPrice);
          const relativeError = errorAbs / actualPrice;
          
          matches.push({
            timestamp: forecastDate.getTime(),
            predicted: predictedPrice,
            actual: actualPrice,
            error: errorAbs,
            relativeError: relativeError,
            date: dateKey
          });
        }
      }
    });

    console.log('有效匹配条数:', matches.length);
    console.log('匹配样本:', matches.slice(0, 5).map(m => ({
      date: m.date,
      predicted: m.predicted.toFixed(2),
      actual: m.actual.toFixed(2),
      error: m.error.toFixed(2),
      relativeError: (m.relativeError * 100).toFixed(2) + '%'
    })));

    if (matches.length === 0) {
      error.value = '没有找到匹配的预测和实际数据';
      return;
    }

    // 计算MAE (Mean Absolute Error)
    mae.value = matches.reduce((sum, match) => sum + match.error, 0) / matches.length;

    // 计算RMSE (Root Mean Square Error)
    const mse = matches.reduce((sum, match) => sum + Math.pow(match.error, 2), 0) / matches.length;
    rmse.value = Math.sqrt(mse);

    // 计算准确率 (基于相对误差小于10%的比例，5%可能过于严格)
    const threshold = 0.10; // 10%的容错率
    const accurateCount = matches.filter(match => match.relativeError < threshold).length;
    accuracy.value = matches.length > 0 ? accurateCount / matches.length : 0;
    
    // 调试输出
    console.log('准确率计算详情:');
    console.log('总匹配数:', matches.length);
    console.log(`误差小于${threshold * 100}%的数量:`, accurateCount);
    console.log('相对误差分布:', {
      '0-1%': matches.filter(m => m.relativeError < 0.01).length,
      '1-5%': matches.filter(m => m.relativeError >= 0.01 && m.relativeError < 0.05).length,
      '5-10%': matches.filter(m => m.relativeError >= 0.05 && m.relativeError < 0.10).length,
      '10-20%': matches.filter(m => m.relativeError >= 0.10 && m.relativeError < 0.20).length,
      '>20%': matches.filter(m => m.relativeError >= 0.20).length
    });
    console.log('相对误差样本:', matches.slice(0, 10).map(m => ({
      predicted: m.predicted.toFixed(2),
      actual: m.actual.toFixed(2),
      relativeError: (m.relativeError * 100).toFixed(2) + '%'
    })));
    console.log('计算的准确率:', (accuracy.value * 100).toFixed(2) + '%');

    // 计算趋势准确率
    // 首先按时间排序
    matches.sort((a, b) => a.timestamp - b.timestamp);
    
    let trendCorrectCount = 0;
    for (let i = 1; i < matches.length; i++) {
      const actualTrend = matches[i].actual > matches[i-1].actual ? 'up' : 'down';
      const predictedTrend = matches[i].predicted > matches[i-1].predicted ? 'up' : 'down';
      if (actualTrend === predictedTrend) {
        trendCorrectCount++;
      }
    }
    trendAccuracy.value = matches.length > 1 ? trendCorrectCount / (matches.length - 1) : 0;
    
    console.log('趋势准确率计算详情:');
    console.log('趋势比较总数:', matches.length - 1);
    console.log('趋势预测正确数:', trendCorrectCount);
    console.log('趋势准确率:', (trendAccuracy.value * 100).toFixed(2) + '%');

    return matches;
  } catch (err) {
    console.error('计算准确性指标失败:', err);
    error.value = '计算准确性指标时发生错误';
    return [];
  }
}

// 创建预测vs实际价格对比图表
function createComparisonChart(matches) {
  console.log('开始创建对比图表...');
  console.log('chartRef.value:', chartRef.value);
  console.log('matches length:', matches.length);
  
  if (!chartRef.value || !matches.length) {
    console.log('图表容器或数据不存在');
    return;
  }

  try {
    const option = {
      title: {
        text: '预测价格 vs 实际价格',
        left: 'center',
        textStyle: { fontSize: 16, fontWeight: 'normal' }
      },
      tooltip: {
        trigger: 'axis',
        formatter: function(params) {
          if (!params || params.length < 2) return '';
          const date = new Date(params[0].value[0]).toLocaleDateString();
          return `${date}<br/>
                  实际价格: $${params[0].value[1].toFixed(4)}<br/>
                  预测价格: $${params[1].value[1].toFixed(4)}<br/>
                  误差: $${Math.abs(params[0].value[1] - params[1].value[1]).toFixed(4)}`;
        }
      },
      legend: {
        data: ['实际价格', '预测价格'],
        top: 30
      },
      xAxis: {
        type: 'time',
        name: '时间'
      },
      yAxis: {
        type: 'value',
        name: '价格 ($)',
        scale: true
      },
      series: [
        {
          name: '实际价格',
          type: 'line',
          data: matches.map(m => [m.timestamp, m.actual]),
          itemStyle: { color: '#5470c6' },
          symbol: 'circle',
          symbolSize: 6
        },
        {
          name: '预测价格',
          type: 'line',
          data: matches.map(m => [m.timestamp, m.predicted]),
          itemStyle: { color: '#ff6b6b' },
          lineStyle: { type: 'dashed' },
          symbol: 'diamond',
          symbolSize: 6
        }
      ]
    };

    if (chartInstance) {
      chartInstance.dispose();
    }
    
    console.log('正在初始化图表...');
    chartInstance = echarts.init(chartRef.value);
    chartInstance.setOption(option);
    console.log('图表初始化完成');
    
    // 强制调整大小
    setTimeout(() => {
      if (chartInstance) {
        chartInstance.resize();
      }
    }, 100);
    
  } catch (err) {
    console.error('创建对比图表时出错:', err);
  }
}

// 创建误差分布图表
function createErrorDistributionChart(matches) {
  console.log('开始创建误差分布图表...');
  if (!errorChartRef.value || !matches.length) {
    console.log('误差图表容器或数据不存在');
    return;
  }

  try {
    // 计算误差百分比分布
    const errorPercentages = matches.map(m => m.relativeError * 100);
    
    // 创建误差区间
    const bins = [0, 1, 2, 3, 5, 10, 20, 50];
    const distribution = new Array(bins.length - 1).fill(0);
    
    errorPercentages.forEach(error => {
      for (let i = 0; i < bins.length - 1; i++) {
        if (error >= bins[i] && error < bins[i + 1]) {
          distribution[i]++;
          break;
        }
      }
    });

    const option = {
      title: {
        text: '误差分布 (%)',
        left: 'center',
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      xAxis: {
        type: 'category',
        data: bins.slice(0, -1).map((bin, i) => `${bin}-${bins[i + 1]}%`)
      },
      yAxis: {
        type: 'value',
        name: '频次'
      },
      series: [{
        type: 'bar',
        data: distribution,
        itemStyle: {
          color: function(params) {
            const colors = ['#67C23A', '#85CE61', '#F0A020', '#F56C6C', '#909399'];
            return colors[Math.min(params.dataIndex, colors.length - 1)];
          }
        }
      }]
    };

    if (errorChartInstance) {
      errorChartInstance.dispose();
    }
    
    console.log('正在初始化误差分布图表...');
    errorChartInstance = echarts.init(errorChartRef.value);
    errorChartInstance.setOption(option);
    console.log('误差分布图表初始化完成');
    
    // 强制调整大小
    setTimeout(() => {
      if (errorChartInstance) {
        errorChartInstance.resize();
      }
    }, 100);
    
  } catch (err) {
    console.error('创建误差分布图表时出错:', err);
  }
}

// 更新图表
async function updateCharts() {
  console.log('开始更新图表...');
  isLoading.value = true;
  error.value = null;

  await nextTick();

  try {
    const matches = calculateAccuracyMetrics();
    console.log('计算结果:', matches ? matches.length : 0, '条匹配数据');
    
    if (matches && matches.length > 0) {
      // 等待DOM更新
      await nextTick();
      
      // 确保DOM元素存在后再创建图表
      console.log('DOM元素检查 - chartRef:', !!chartRef.value, 'errorChartRef:', !!errorChartRef.value);
      
      if (chartRef.value && errorChartRef.value) {
        console.log('开始创建图表...');
        createComparisonChart(matches);
        createErrorDistributionChart(matches);
      } else {
        console.log('DOM元素尚未准备好，延迟重试...');
        setTimeout(() => {
          if (chartRef.value && errorChartRef.value) {
            createComparisonChart(matches);
            createErrorDistributionChart(matches);
          }
        }, 200);
      }
    }
  } catch (err) {
    console.error('更新图表失败:', err);
    error.value = '图表更新失败: ' + err.message;
  }

  isLoading.value = false;
}

// 响应式更新
watch([() => props.forecastData, () => props.actualData], () => {
  if (props.forecastData.length > 0 && props.actualData.length > 0) {
    updateCharts();
  }
}, { deep: true });

onMounted(async () => {
  console.log('组件挂载，开始初始化...');
  console.log('Props - forecastData length:', props.forecastData.length);
  console.log('Props - actualData length:', props.actualData.length);
  
  await nextTick();
  
  // 延迟确保DOM完全渲染
  setTimeout(async () => {
    console.log('延迟执行，检查DOM状态...');
    console.log('chartRef:', !!chartRef.value);
    console.log('errorChartRef:', !!errorChartRef.value);
    
    if (props.forecastData.length > 0 && props.actualData.length > 0) {
      await updateCharts();
    } else {
      console.log('数据不足，等待数据更新...');
    }
  }, 300);
});

// 组件卸载时清理图表实例
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
  if (errorChartInstance) {
    errorChartInstance.dispose();
    errorChartInstance = null;
  }
});
</script>

<style scoped>
.accuracy-analysis-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.chart-header {
  text-align: center;
  margin-bottom: 24px;
}

.chart-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.chart-subtitle {
  color: #666;
  margin: 0;
  font-size: 14px;
}

.loading-state, .error-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.metric-card {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e1e5ff;
}

.metric-icon {
  font-size: 32px;
  margin-right: 16px;
}

.metric-info {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  margin-top: 4px;
}

.chart-container {
  margin-bottom: 32px;
}

.chart {
  width: 100%;
  height: 400px;
}

.error-distribution h4 {
  color: #333;
  margin-bottom: 16px;
  font-size: 16px;
}

.error-chart {
  width: 100%;
  height: 300px;
}

@media (max-width: 768px) {
  .metrics-row {
    grid-template-columns: 1fr;
  }
  
  .metric-card {
    padding: 16px;
  }
  
  .chart {
    height: 300px;
  }
  
  .error-chart {
    height: 250px;
  }
}
</style>
