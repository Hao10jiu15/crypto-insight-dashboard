<template>
  <div class="volatility-analysis-container">
    <div class="chart-header">
      <h3>📊 波动性分析</h3>
      <p class="chart-description">分析不同货币的价格波动性和风险特征</p>
    </div>
    
    <div class="chart-controls">
      <select v-model="selectedTimeframe" @change="fetchVolatilityData" class="timeframe-select">
        <option value="7d">7天</option>
        <option value="30d">30天</option>
        <option value="90d">90天</option>
      </select>
    </div>

    <div class="volatility-overview" v-if="volatilityStats">
      <div class="overview-card">
        <h4>📈 最高波动性</h4>
        <div class="currency-item">
          <span class="currency-name">{{ volatilityStats.highest.name }}</span>
          <span class="volatility-value high">{{ volatilityStats.highest.volatility }}%</span>
        </div>
      </div>
      <div class="overview-card">
        <h4>📉 最低波动性</h4>
        <div class="currency-item">
          <span class="currency-name">{{ volatilityStats.lowest.name }}</span>
          <span class="volatility-value low">{{ volatilityStats.lowest.volatility }}%</span>
        </div>
      </div>
      <div class="overview-card">
        <h4>📊 平均波动性</h4>
        <div class="currency-item">
          <span class="volatility-value average">{{ volatilityStats.average }}%</span>
        </div>
      </div>
    </div>

    <div ref="chartContainer" class="chart-container">
      <div v-if="loading" class="loading-spinner">
        <div class="spinner"></div>
        <span>分析波动性数据中...</span>
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
  name: 'VolatilityAnalysisChart',
  data() {
    return {
      chart: null,
      loading: true,
      error: null,
      selectedTimeframe: '30d',
      currencies: [],
      volatilityStats: null
    }
  },
  async mounted() {
    await this.initChart()
    await this.loadCurrencies()
    await this.fetchVolatilityData()
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
        this.currencies = response.data.slice(0, 10) // 只分析前10个货币
      } catch (error) {
        console.error('获取货币列表失败:', error)
      }
    },

    async fetchVolatilityData() {
      this.loading = true
      this.error = null

      try {
        const days = parseInt(this.selectedTimeframe.replace('d', ''))
        const endDate = new Date()
        const startDate = new Date()
        startDate.setDate(startDate.getDate() - days)

        const volatilityData = []

        for (const currency of this.currencies) {
          try {
            const response = await getMarketData({
              currency_id: currency.coingecko_id,
              start_date: startDate.toISOString().split('T')[0],
              end_date: endDate.toISOString().split('T')[0]
            })

            if (response.data && response.data.data.length > 1) {
              const prices = response.data.data.map(item => item[2]) // 收盘价
              const returns = this.calculateReturns(prices)
              const volatility = this.calculateVolatility(returns)
              const drawdown = this.calculateMaxDrawdown(prices)
              
              volatilityData.push({
                name: currency.name,
                symbol: currency.symbol,
                volatility: volatility,
                drawdown: drawdown,
                risk: this.calculateRiskScore(volatility, drawdown)
              })
            }
          } catch (error) {
            console.warn(`获取${currency.name}数据失败:`, error)
          }
        }

        if (volatilityData.length === 0) {
          this.error = '暂无可分析的波动性数据'
          return
        }

        this.calculateVolatilityStats(volatilityData)
        this.renderChart(volatilityData)

      } catch (error) {
        this.error = '获取波动性数据失败: ' + error.message
        console.error('获取波动性数据失败:', error)
      } finally {
        this.loading = false
      }
    },

    calculateReturns(prices) {
      const returns = []
      for (let i = 1; i < prices.length; i++) {
        const return_rate = (prices[i] - prices[i-1]) / prices[i-1]
        returns.push(return_rate)
      }
      return returns
    },

    calculateVolatility(returns) {
      if (returns.length === 0) return 0
      
      const mean = returns.reduce((sum, r) => sum + r, 0) / returns.length
      const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length
      const volatility = Math.sqrt(variance) * Math.sqrt(365) * 100 // 年化波动率
      
      return parseFloat(volatility.toFixed(2))
    },

    calculateMaxDrawdown(prices) {
      let maxDrawdown = 0
      let peak = prices[0]
      
      for (let i = 1; i < prices.length; i++) {
        if (prices[i] > peak) {
          peak = prices[i]
        } else {
          const drawdown = (peak - prices[i]) / peak
          maxDrawdown = Math.max(maxDrawdown, drawdown)
        }
      }
      
      return parseFloat((maxDrawdown * 100).toFixed(2))
    },

    calculateRiskScore(volatility, drawdown) {
      // 简单的风险评分: 波动率 + 最大回撤
      return parseFloat((volatility * 0.6 + drawdown * 0.4).toFixed(2))
    },

    calculateVolatilityStats(data) {
      if (data.length === 0) return

      const volatilities = data.map(item => item.volatility)
      const highest = data.reduce((max, item) => item.volatility > max.volatility ? item : max)
      const lowest = data.reduce((min, item) => item.volatility < min.volatility ? item : min)
      const average = (volatilities.reduce((sum, v) => sum + v, 0) / volatilities.length).toFixed(2)

      this.volatilityStats = {
        highest: { name: highest.name, volatility: highest.volatility },
        lowest: { name: lowest.name, volatility: lowest.volatility },
        average: average
      }
    },

    renderChart(data) {
      // 准备散点图数据 [volatility, drawdown, risk, name]
      const scatterData = data.map(item => ({
        value: [item.volatility, item.drawdown, item.risk],
        name: item.symbol,
        itemStyle: {
          color: this.getRiskColor(item.risk)
        }
      }))

      // 准备柱状图数据
      const barData = data.sort((a, b) => b.volatility - a.volatility)

      const option = {
        title: [
          {
            text: '波动性 vs 最大回撤',
            left: '25%',
            top: '5%',
            textAlign: 'center',
            textStyle: { fontSize: 14 }
          },
          {
            text: '波动性排名',
            right: '25%',
            top: '5%',
            textAlign: 'center',
            textStyle: { fontSize: 14 }
          }
        ],
        tooltip: [
          {
            trigger: 'item',
            formatter: function(params) {
              const [volatility, drawdown, risk] = params.value
              return `${params.name}<br/>
                      波动率: ${volatility}%<br/>
                      最大回撤: ${drawdown}%<br/>
                      风险评分: ${risk}`
            }
          },
          {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            formatter: function(params) {
              const item = params[0]
              return `${item.name}<br/>波动率: ${item.value}%`
            }
          }
        ],
        grid: [
          {
            left: '5%',
            right: '55%',
            top: '15%',
            bottom: '10%'
          },
          {
            left: '55%',
            right: '5%',
            top: '15%',
            bottom: '10%'
          }
        ],
        xAxis: [
          {
            type: 'value',
            name: '年化波动率 (%)',
            nameLocation: 'middle',
            nameGap: 30,
            gridIndex: 0
          },
          {
            type: 'category',
            data: barData.map(item => item.symbol),
            gridIndex: 1,
            axisLabel: {
              rotate: 45
            }
          }
        ],
        yAxis: [
          {
            type: 'value',
            name: '最大回撤 (%)',
            nameLocation: 'middle',
            nameGap: 40,
            gridIndex: 0
          },
          {
            type: 'value',
            name: '波动率 (%)',
            gridIndex: 1
          }
        ],
        visualMap: {
          min: Math.min(...data.map(item => item.risk)),
          max: Math.max(...data.map(item => item.risk)),
          calculable: true,
          orient: 'vertical',
          left: '2%',
          top: 'middle',
          text: ['高风险', '低风险'],
          inRange: {
            color: ['#50C878', '#FFD700', '#FF6347']
          }
        },
        series: [
          {
            name: '风险分布',
            type: 'scatter',
            xAxisIndex: 0,
            yAxisIndex: 0,
            data: scatterData,
            symbolSize: 20,
            label: {
              show: true,
              position: 'top',
              formatter: '{b}',
              fontSize: 10
            },
            emphasis: {
              symbolSize: 30
            }
          },
          {
            name: '波动率',
            type: 'bar',
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: barData.map(item => ({
              value: item.volatility,
              name: item.symbol,
              itemStyle: {
                color: this.getRiskColor(item.risk)
              }
            })),
            label: {
              show: true,
              position: 'top',
              formatter: '{c}%'
            }
          }
        ]
      }

      this.chart.setOption(option)
    },

    getRiskColor(risk) {
      if (risk < 20) return '#50C878' // 绿色 - 低风险
      if (risk < 40) return '#FFD700' // 黄色 - 中等风险
      return '#FF6347' // 红色 - 高风险
    }
  }
}
</script>

<style scoped>
.volatility-analysis-container {
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
}

.timeframe-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  font-size: 14px;
}

.volatility-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.overview-card {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.overview-card h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 14px;
}

.currency-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.currency-name {
  font-weight: 500;
}

.volatility-value {
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 4px;
  color: white;
}

.volatility-value.high {
  background: #e74c3c;
}

.volatility-value.low {
  background: #27ae60;
}

.volatility-value.average {
  background: #f39c12;
}

.chart-container {
  height: 500px;
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
