import axios from 'axios';

// 创建一个axios实例，并配置基础URL
// 这样我们所有的请求都会默认指向后端API的地址
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api', // 你的Django后端API地址
  headers: {
    'Content-Type': 'application/json',
  },
});

// 定义并导出一个函数，用于获取货币列表
export const getCurrencies = () => {
  return apiClient.get('/currencies/');
};

/**
 * 获取市场图表数据
 * @param {object} params 查询参数, e.g., { currency_id: 'bitcoin', interval: '1d' }
 * @returns Promise
 */
export const getMarketData = (params) => {
  return apiClient.get('/market_data/', { params });
};

/**
 * 获取单个货币的最新市场指标
 * @param {string} currencyId CoinGecko ID
 * @returns Promise
 */
export const getCurrencyMetrics = (currencyId) => {
  // 注意URL路径匹配后端的路由器设置
  return apiClient.get(`/metrics/${currencyId}/`);
};

/**
 * 获取市值排名前10的货币数据
 * @returns Promise
 */
export const getMarketShare = () => {
  return apiClient.get('/market_share/');
};

/**
 * 获取指定货币的预测数据
 * @param {object} params e.g., { currency_id: 'bitcoin' }
 * @returns Promise
 */
export const getForecastData = (params) => {
  return apiClient.get('/forecasts/', { params });
};

/**
 * 获取指定货币的完整预测数据（包含历史拟合数据）
 * @param {object} params e.g., { currency_id: 'bitcoin' }
 * @returns Promise
 */
export const getCompleteForecastData = (params) => {
  const completeParams = { ...params, include_historical: 'true' };
  return apiClient.get('/forecasts/', { params: completeParams });
};

/**
 * 获取预测模型的组件数据
 * @param {object} params e.g., { currency_id: 'bitcoin' }
 * @returns Promise
 */
export const getForecastComponents = (params) => {
  return apiClient.get('/forecast_components/', { params });
};