<template>
  <a-layout id="app" class="layout">
    <a-layout-header>
      <div class="logo">AUTO - HAOCE</div>
    </a-layout-header>
    <a-layout-content style="padding: 10px;height: 100%;">
      <router-view />
    </a-layout-content>
    <a-layout-footer style="text-align: center">AUTO-HAOCE ©2020 Created by OOOOONLY</a-layout-footer>
  </a-layout>
</template>

<style>

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* text-align: center; */
  color: #2c3e50;
  width: 100%;
}

.logo {
  width: 200px;
  height: 100%;
  float: left;
  color: aliceblue;
  font-size: 18px;
}
</style>
