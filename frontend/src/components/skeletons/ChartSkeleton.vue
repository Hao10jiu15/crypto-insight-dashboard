<template>
    <div class="chart-skeleton-container">
        <div class="skeleton-box"></div>
    </div>
</template>

<style scoped>
@keyframes pulse-bg {
    0% {
        background-color: #f0f0f0;
    }

    50% {
        background-color: #e0e0e0;
    }

    100% {
        background-color: #f0f0f0;
    }
}

.chart-skeleton-container {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    background-color: #fff;
}

.skeleton-box {
    height: 500px;
    /* 与图表高度保持一致 */
    width: 100%;
    border-radius: 6px;
    animation: pulse-bg 1.5s infinite ease-in-out;
}
</style>