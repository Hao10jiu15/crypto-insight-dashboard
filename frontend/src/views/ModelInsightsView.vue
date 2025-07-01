<template>
  <div class="model-insights-view">
    <div class="page-header">
      <h1>🧠 模型洞察分析</h1>
      <p class="page-description">深入分析加密货币市场趋势和模型预测效果</p>
    </div>

    <div class="insights-grid">
      <!-- 相关性分析 -->
      <div class="grid-item full-width">
        <CorrelationHeatmapChart />
      </div>

      <!-- 波动性分析 -->
      <div class="grid-item full-width">
        <VolatilityAnalysisChart />
      </div>

      <!-- 市场概览卡片 -->
      <div class="grid-item">
        <div class="insight-card">
          <h3>📈 市场表现概览</h3>
          <div class="market-overview">
            <div class="overview-item" v-for="metric in marketOverview" :key="metric.label">
              <div class="metric-label">{{ metric.label }}</div>
              <div class="metric-value" :class="metric.trend">
                {{ metric.value }}
                <span class="trend-icon">{{ metric.icon }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 预测置信度 -->
      <div class="grid-item">
        <div class="insight-card">
          <h3>🎯 预测置信度</h3>
          <div class="confidence-chart" ref="confidenceChart"></div>
        </div>
      </div>

      <!-- 关键指标 -->
      <div class="grid-item full-width">
        <div class="insight-card">
          <h3>🔍 关键市场指标</h3>
          <div class="key-metrics">
            <div class="metric-item" v-for="indicator in keyIndicators" :key="indicator.name">
              <div class="indicator-header">
                <span class="indicator-name">{{ indicator.name }}</span>
                <span class="indicator-status" :class="indicator.status">{{ indicator.signal }}</span>
              </div>
              <div class="indicator-description">{{ indicator.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CorrelationHeatmapChart from '@/components/CorrelationHeatmapChart.vue'
import VolatilityAnalysisChart from '@/components/VolatilityAnalysisChart.vue'
import * as echarts from 'echarts'

export default {
  name: 'ModelInsightsView',
  components: {
    CorrelationHeatmapChart,
    VolatilityAnalysisChart
  },
  data() {
    return {
      confidenceChart: null,
      marketOverview: [
        { label: '总市值', value: '加载中...', trend: 'neutral', icon: '📊' },
        { label: '24H成交量', value: '加载中...', trend: 'neutral', icon: '💹' },
        { label: '恐慌指数', value: '加载中...', trend: 'neutral', icon: '😨' },
        { label: 'BTC占比', value: '加载中...', trend: 'neutral', icon: '₿' }
      ],
      keyIndicators: [
        {
          name: '市场趋势',
          signal: '看涨',
          status: 'bullish',
          description: '基于技术指标和价格动量分析，市场整体呈现上涨趋势'
        },
        {
          name: '波动性水平',
          signal: '中等',
          status: 'neutral',
          description: '当前市场波动性处于正常范围，适合中长期投资'
        },
        {
          name: '相关性强度',
          signal: '高相关',
          status: 'warning',
          description: '主要加密货币间相关性较高，系统性风险需要关注'
        },
        {
          name: '预测可信度',
          signal: '良好',
          status: 'bullish',
          description: '模型预测准确率保持在合理范围内，可作为参考依据'
        }
      ]
    }
  },
  mounted() {
    this.initConfidenceChart()
    this.loadMarketOverview()
  },
  beforeUnmount() {
    if (this.confidenceChart) {
      this.confidenceChart.dispose()
    }
  },
  methods: {
    initConfidenceChart() {
      this.confidenceChart = echarts.init(this.$refs.confidenceChart)
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c}% ({d}%)'
        },
        series: [
          {
            name: '预测置信度',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: [
              { value: 75, name: '高置信度', itemStyle: { color: '#27ae60' } },
              { value: 20, name: '中等置信度', itemStyle: { color: '#f39c12' } },
              { value: 5, name: '低置信度', itemStyle: { color: '#e74c3c' } }
            ]
          }
        ]
      }
      
      this.confidenceChart.setOption(option)
      
      window.addEventListener('resize', () => {
        if (this.confidenceChart) {
          this.confidenceChart.resize()
        }
      })
    },

    async loadMarketOverview() {
      try {
        // 这里可以调用实际的API获取市场数据
        // 为了演示，使用模拟数据
        setTimeout(() => {
          this.marketOverview = [
            { 
              label: '总市值', 
              value: '$2.13T', 
              trend: 'bullish', 
              icon: '📊' 
            },
            { 
              label: '24H成交量', 
              value: '$85.4B', 
              trend: 'bearish', 
              icon: '💹' 
            },
            { 
              label: '恐慌指数', 
              value: '62', 
              trend: 'neutral', 
              icon: '😨' 
            },
            { 
              label: 'BTC占比', 
              value: '42.3%', 
              trend: 'bullish', 
              icon: '₿' 
            }
          ]
        }, 1000)
      } catch (error) {
        console.error('加载市场概览失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.model-insights-view {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  color: #2c3e50;
  font-size: 32px;
  margin-bottom: 10px;
}

.page-description {
  color: #7f8c8d;
  font-size: 16px;
  margin: 0;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.grid-item.full-width {
  grid-column: 1 / -1;
}

.insight-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  height: 100%;
}

.insight-card h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 18px;
}

.market-overview {
  display: grid;
  grid-template-columns: 1fr;
  gap: 15px;
}

.overview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.metric-label {
  color: #666;
  font-size: 14px;
}

.metric-value {
  font-weight: bold;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.metric-value.bullish {
  color: #27ae60;
}

.metric-value.bearish {
  color: #e74c3c;
}

.metric-value.neutral {
  color: #f39c12;
}

.trend-icon {
  font-size: 18px;
}

.confidence-chart {
  height: 200px;
}

.key-metrics {
  display: grid;
  gap: 15px;
}

.metric-item {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.indicator-name {
  font-weight: bold;
  color: #2c3e50;
}

.indicator-status {
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.indicator-status.bullish {
  background: #d5f4e6;
  color: #27ae60;
}

.indicator-status.bearish {
  background: #fdeaea;
  color: #e74c3c;
}

.indicator-status.neutral {
  background: #fef9e7;
  color: #f39c12;
}

.indicator-status.warning {
  background: #fff2e0;
  color: #e67e22;
}

.indicator-description {
  color: #666;
  font-size: 14px;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .insights-grid {
    grid-template-columns: 1fr;
    padding: 0 10px;
  }
  
  .model-insights-view {
    padding: 10px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .grid-item.full-width {
    grid-column: 1;
  }
}
</style>
