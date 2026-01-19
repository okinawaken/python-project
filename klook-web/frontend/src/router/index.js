import {createRouter, createWebHistory} from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home,
    },
    {
        path: '/config',
        name: 'Config',
        component: () => import('../views/ConfigView.vue'),
    },
    {
        path: '/program',
        name: 'Program',
        component: () => import('../views/ProgramView.vue'),
    },
    {
        path: '/task',
        name: 'Task',
        component: () => import('../views/TaskView.vue'),
    },
    {
        path: '/log',
        name: 'Log',
        component: () => import('../views/LogView.vue'),
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router