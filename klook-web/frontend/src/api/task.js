import axios from 'axios'

const API_BASE = '/api'

/**
 * 任务管理 API
 */
export const taskApi = {
    /**
     * 获取所有任务列表
     */
    async getAll(params = {}) {
        const response = await axios.get(`${API_BASE}/tasks`, {params})
        return response.data
    },

    /**
     * 根据 ID 获取任务
     */
    async getById(id) {
        const response = await axios.get(`${API_BASE}/tasks/${id}`)
        return response.data
    },

    /**
     * 创建任务
     */
    async create(task) {
        const response = await axios.post(`${API_BASE}/tasks`, task)
        return response.data
    },

    /**
     * 更新任务
     */
    async update(id, task) {
        const response = await axios.put(`${API_BASE}/tasks/${id}`, task)
        return response.data
    },

    /**
     * 启动任务
     */
    async start(id) {
        const response = await axios.post(`${API_BASE}/tasks/${id}/start`)
        return response.data
    },

    /**
     * 取消任务
     */
    async cancel(id) {
        const response = await axios.post(`${API_BASE}/tasks/${id}/cancel`)
        return response.data
    },

    /**
     * 删除任务
     */
    async delete(id) {
        await axios.delete(`${API_BASE}/tasks/${id}`)
    },

    /**
     * 获取任务统计信息
     */
    async getStats() {
        const response = await axios.get(`${API_BASE}/tasks/stats/summary`)
        return response.data
    }
}
