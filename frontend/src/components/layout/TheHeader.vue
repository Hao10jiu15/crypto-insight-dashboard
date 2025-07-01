<template>
    <header class="app-header">
        <router-link to="/" class="title-link">
            <h1>Crypto Insight Dashboard</h1>
        </router-link>
    </header>
</template>

<style scoped>
.app-header {
    grid-area: header;
    background-color: #ffffff;
    padding: 0 30px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #e0e0e0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    z-index: 10;
    /* 确保header在最上层 */
}

.app-header h1 {
    font-size: 24px;
    color: #333;
    margin: 0;
}

.title-link {
    text-decoration: none;
    color: inherit;
    outline: none;
    border: none;
    background: none;
    cursor: pointer;
}

.title-link:hover {
    text-decoration: none;
    color: inherit;
    background: none;
}

.title-link:focus {
    outline: none;
    box-shadow: none;
    background: none;
}

.title-link:active {
    background: none;
    color: inherit;
}
</style>