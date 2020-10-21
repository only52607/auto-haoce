import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Antd from 'ant-design-vue'
import api from "@/utils/api.js"
import { createFromIconfontCN } from '@ant-design/icons-vue'
import 'ant-design-vue/dist/antd.css'
import bookStore from "@/utils/books.js";
// import VueAwesomeSwiper from 'vue-awesome-swiper'
// import 'swiper/swiper-bundle.css'

let app = createApp(App)
app.config.globalProperties.$api = api
app.config.globalProperties.$books = bookStore.books
app.use(router)
app.use(Antd)
// app.use(VueAwesomeSwiper)
app.component("IconFont",createFromIconfontCN({
    scriptUrl: '//at.alicdn.com/t/font_2142009_0e7zltvke857.js',
}))
app.mount('#app')