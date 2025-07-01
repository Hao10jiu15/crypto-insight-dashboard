<template>
    <div class="metrics-grid">
        <div v-for="n in 5" :key="n" class="metric-card-skeleton">
            <div class="skeleton-line label"></div>
            <div class="skeleton-line value"></div>
        </div>
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

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.metric-card-skeleton {
    background-color: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.skeleton-line {
    border-radius: 4px;
    animation: pulse-bg 1.5s infinite ease-in-out;
}

.label {
    height: 14px;
    width: 60%;
    margin-bottom: 12px;
}

.value {
    height: 24px;
    width: 80%;
}
</style>