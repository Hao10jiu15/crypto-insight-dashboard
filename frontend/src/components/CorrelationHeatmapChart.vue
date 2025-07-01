<template>
  <div class="correlation-heatmap-container">
    <div class="chart-header">
      <h3>🔗 货币相关性分析</h3>
      <p class="chart-description">显示不同加密货币之间的价格相关性</p>
    </div>
    
    <div class="chart-controls">
      <select v-model="selectedTimeframe" @change="fetchCorrelationData" class="timeframe-select">
        <option value="30d">30天</option>
        <option value="90d">90天</option>
        <option value="180d">180天</option>
        <option value="365d">1年</option>
      </select>
    </div>

    <div ref="chartContainer" class="chart-container">
      <div v-if="loading" class="loading-spinner">
        <div class="spinner"></div>
        <span>加载相关性数据中...</span>
      </div>
      <div v-else-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import { getCurrencies, getMarketData } from '@/services/api'
import * as echarts from 'echarts'

export default {
  name: 'CorrelationHeatmapChart',
  data() {
    return {
      chart: null,
      loading: true,
      error: null,
      selectedTimeframe: '30d',
      correlationData: [],
      currencies: []
    }
  },
  async mounted() {
    await this.initChart()
    await this.loadCurrencies()
    await this.fetchCorrelationData()
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.dispose()
    }
  },
  methods: {
    async initChart() {
      this.chart = echarts.init(this.$refs.chartContainer)
      
      window.addEventListener('resize', () => {
        if (this.chart) {
          this.chart.resize()
        }
      })
    },

    async loadCurrencies() {
      try {
        const response = await getCurrencies()
        this.currencies = response.data.slice(0, 8) // 只取前8个货币
      } catch (error) {
        console.error('获取货币列表失败:', error)
      }
    },

    async fetchCorrelationData() {
      this.loading = true
      this.error = null

      try {
        // 计算时间范围
        const endDate = new Date()
        const startDate = new Date()
        const days = parseInt(this.selectedTimeframe.replace('d', ''))
        startDate.setDate(startDate.getDate() - days)

        // 获取所有货币的价格数据
        const priceData = {}
        for (const currency of this.currencies) {
          try {
            const response = await getMarketData({
              currency_id: currency.coingecko_id,
              start_date: startDate.toISOString().split('T')[0],
              end_date: endDate.toISOString().split('T')[0]
            })
            
            if (response.data && response.data.data.length > 0) {
              // 提取收盘价格数据 (索引2是收盘价)
              priceData[currency.coingecko_id] = response.data.data.map(item => item[2])
            }
          } catch (error) {
            console.warn(`获取${currency.name}数据失败:`, error)
          }
        }

        // 计算相关性矩阵
        const correlationMatrix = this.calculateCorrelationMatrix(priceData)
        this.renderChart(correlationMatrix)
      } catch (error) {
        this.error = '获取相关性数据失败: ' + error.message
        console.error('获取相关性数据失败:', error)
      } finally {
        this.loading = false
      }
    },

    calculateCorrelationMatrix(priceData) {
      const currencies = Object.keys(priceData)
      const matrix = []

      for (let i = 0; i < currencies.length; i++) {
        for (let j = 0; j < currencies.length; j++) {
          const curr1 = currencies[i]
          const curr2 = currencies[j]
          
          if (curr1 === curr2) {
            matrix.push([i, j, 1]) // 自相关为1
          } else {
            const correlation = this.calculatePearsonCorrelation(
              priceData[curr1], 
              priceData[curr2]
            )
            matrix.push([i, j, correlation])
          }
        }
      }

      return { matrix, currencies }
    },

    calculatePearsonCorrelation(x, y) {
      if (!x || !y || x.length !== y.length || x.length === 0) {
        return 0
      }

      const n = x.length
      let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0, sumY2 = 0

      for (let i = 0; i < n; i++) {
        sumX += x[i]
        sumY += y[i]
        sumXY += x[i] * y[i]
        sumX2 += x[i] * x[i]
        sumY2 += y[i] * y[i]
      }

      const numerator = n * sumXY - sumX * sumY
      const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY))

      return denominator === 0 ? 0 : numerator / denominator
    },

    renderChart({ matrix, currencies }) {
      const currencyNames = currencies.map(id => {
        const currency = this.currencies.find(c => c.coingecko_id === id)
        return currency ? currency.symbol : id.toUpperCase()
      })

      const option = {
        title: {
          text: '货币相关性热力图',
          left: 'center',
          textStyle: {
            fontSize: 16,
            color: '#333'
          }
        },
        tooltip: {
          position: 'top',
          formatter: function(params) {
            const [i, j, correlation] = params.data
            return `${currencyNames[i]} vs ${currencyNames[j]}<br/>相关性: ${correlation.toFixed(3)}`
          }
        },
        grid: {
          left: '10%',
          right: '10%',
          top: '15%',
          bottom: '15%'
        },
        xAxis: {
          type: 'category',
          data: currencyNames,
          splitArea: {
            show: true
          },
          axisLabel: {
            fontSize: 12
          }
        },
        yAxis: {
          type: 'category',
          data: currencyNames,
          splitArea: {
            show: true
          },
          axisLabel: {
            fontSize: 12
          }
        },
        visualMap: {
          min: -1,
          max: 1,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '5%',
          inRange: {
            color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
          }
        },
        series: [{
          name: '相关性',
          type: 'heatmap',
          data: matrix,
          label: {
            show: true,
            formatter: function(params) {
              return params.data[2].toFixed(2)
            }
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }

      this.chart.setOption(option)
    }
  }
}
</script>

<style scoped>
.correlation-heatmap-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.chart-header {
  margin-bottom: 15px;
}

.chart-header h3 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 18px;
}

.chart-description {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

.chart-controls {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.timeframe-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  font-size: 14px;
}

.chart-container {
  height: 400px;
  position: relative;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #e74c3c;
  font-size: 16px;
}
</style>
