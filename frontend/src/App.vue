<script setup>
import TheHeader from './components/layout/TheHeader.vue';
import TheSidebar from './components/layout/TheSidebar.vue';
</script>

<template>
  <div id="dashboard-layout">
    <TheHeader />
    <TheSidebar />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style>
/* 样式保持不变 */
body {
  margin: 0;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  background-color: #f4f7f6;
}

#dashboard-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  grid-template-rows: 64px 1fr;
  grid-template-areas: "header header" "sidebar main";
  height: 100vh;
  width: 100vw;
  overflow: hidden; /* 防止整体页面出现滚动条 */
}

.main-content {
  grid-area: main;
  overflow-y: auto;
  overflow-x: hidden; /* 防止横向滚动条 */
  padding: 30px;
  max-width: calc(100vw - 240px - 60px); /* 减去侧边栏宽度和内边距 */
  box-sizing: border-box;
}
</style>