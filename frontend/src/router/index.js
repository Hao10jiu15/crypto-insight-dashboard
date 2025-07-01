import { createRouter, createWebHashHistory } from 'vue-router';
import CurrencyDetail from '../views/CurrencyDetail.vue';
import CurrencyForecast from '../views/CurrencyForecast.vue';
import DashboardOverview from '../views/DashboardOverview.vue';
import ModelInsightsView from '../views/ModelInsightsView.vue';

const routes = [
  {
    path: '/',
    name: 'Overview',
    component: DashboardOverview,
  },
  {
    path: '/currency/:id', // :id 是一个动态参数
    name: 'Detail',
    component: CurrencyDetail,
    props: true, // 将路由参数作为props传递给组件
  },
  {
    path: '/forecast/:id', // :id 是 coingecko_id
    name: 'Forecast',
    component: CurrencyForecast,
    props: true,
  },
  {
    path: '/insights',
    name: 'ModelInsights',
    component: ModelInsightsView,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;