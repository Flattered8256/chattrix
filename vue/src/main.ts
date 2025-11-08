import { createApp } from "vue";
import { createPinia } from "pinia";
import router from "./router";
import "./styles/global.scss"; // 导入全局样式
import App from "./App.vue";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.mount("#app");
