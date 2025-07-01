import { defineStore } from 'pinia';
import { ref } from 'vue';
import { getCurrencies } from '../services/api';

export const useMainStore = defineStore('main', () => {
    // --- State ---
    // 所有可用货币的列表
    const currencies = ref([]);
    // 用户当前选中的货币ID
    const selectedCurrencyId = ref(null);
    const isLoading = ref(true);
    const error = ref(null);

    // --- Actions ---
    // 从API获取所有货币的列表
    async function fetchCurrencies() {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await getCurrencies();
            if (response.data && response.data.length > 0) {
                currencies.value = response.data;
                // 默认选中列表中的第一个货币
                selectedCurrencyId.value = response.data[0].id;
            }
        } catch (err) {
            console.error("获取货币列表失败:", err);
            error.value = "无法加载货币列表。";
        } finally {
            isLoading.value = false;
        }
    }

    // --- Expose State and Actions ---
    return {
        currencies,
        selectedCurrencyId,
        isLoading,
        error,
        fetchCurrencies,
    };
});