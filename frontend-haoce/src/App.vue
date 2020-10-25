<template>
  <a-layout id="app" class="layout">
    <a-layout-header class="header">
      <div class="logo"> <read-outlined /> AUTO - HAOCE</div>
    </a-layout-header>
    <a-layout-content class="content">
      <router-view />
    </a-layout-content>
    <a-layout-footer class="footer" >AUTO-HAOCE ©2020 Created by OOOOONLY</a-layout-footer>
  </a-layout>
</template>

<script>
import { ReadOutlined } from "@ant-design/icons-vue";
export default {
  components:{
    ReadOutlined
  }
}
</script>

<style>

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* text-align: center; */
  color: #2c3e50;
  width: 100%;
}

.header {
  position: fixed;
  z-index: 1; 
  width:100%;
}

.content {
  margin-top: 64px;
  padding: 10px;
  height: 100%;
}

.logo {
  width: 200px;
  height: 100%;
  float: left;
  color: aliceblue;
  font-size: 18px;
}

.footer {
  text-align: center
}
</style>
