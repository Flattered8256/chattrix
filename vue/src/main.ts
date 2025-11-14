import { createApp } from "vue";
import { createPinia } from "pinia";
import router from "./router";
import "./styles/global.scss"; // 导入全局样式
import App from "./App.vue";

// 引入 Element Plus
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(ElementPlus); // 注册 Element Plus
app.mount("#app");
