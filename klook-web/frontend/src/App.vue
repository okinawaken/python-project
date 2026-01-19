<template>
  <div id="app">
    <el-container style="height: 100vh">
      <el-header style="background-color: #409EFF; color: white; line-height: 60px; padding: 0 20px;">
        <div style="display: flex; align-items: center; justify-content: space-between; height: 100%">
          <h2
              style="margin: 0; cursor: pointer; user-select: none;"
              @click="goHome"
              title="点击返回主页"
          >
            Klook Web - 抢购助手
          </h2>
          <el-space :size="15">
            <el-button
                :type="currentRoute === '/' ? 'warning' : 'primary'"
                :plain="currentRoute !== '/'"
                @click="router.push('/')"
                size="default"
            >
              首页
            </el-button>
            <el-button
                :type="currentRoute === '/config' ? 'warning' : 'primary'"
                :plain="currentRoute !== '/config'"
                @click="router.push('/config')"
                size="default"
            >
              配置管理
            </el-button>
            <el-button
                :type="currentRoute === '/program' ? 'warning' : 'primary'"
                :plain="currentRoute !== '/program'"
                @click="router.push('/program')"
                size="default"
            >
              优惠券项目
            </el-button>
            <el-button
                :type="currentRoute === '/task' ? 'warning' : 'primary'"
                :plain="currentRoute !== '/task'"
                @click="router.push('/task')"
                size="default"
            >
              任务管理
            </el-button>
            <el-button
                :type="currentRoute === '/log' ? 'warning' : 'primary'"
                :plain="currentRoute !== '/log'"
                @click="router.push('/log')"
                size="default"
            >
              日志查看
            </el-button>
          </el-space>
        </div>
      </el-header>
      <el-main>
        <router-view/>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import {useRoute, useRouter} from 'vue-router'
import {computed} from 'vue'

const router = useRouter()
const route = useRoute()

const currentRoute = computed(() => route.path)

const goHome = () => {
  router.push('/')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>