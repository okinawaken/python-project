import axios from 'axios'

const API_BASE = '/api'

/**
 * 日志管理 API
 */
export const logApi = {
    /**
     * 获取所有日志列表
     * @param {Object} params - 查询参数
     * @param {number} params.task_id - 任务 ID（可选）
     * @param {string} params.level - 日志级别（可选）
     * @param {number} params.limit - 每页数量（默认100）
     * @param {number} params.offset - 偏移量（默认0）
     */
    async getAll(params = {}) {
        const response = await axios.get(`${API_BASE}/logs`, {params})
        return response.data
    },

    /**
     * 根据 ID 获取日志
     * @param {number} id - 日志 ID
     */
    async getById(id) {
        const response = await axios.get(`${API_BASE}/logs/${id}`)
        return response.data
    },

    /**
     * 获取任务的日志列表
     * @param {number} taskId - 任务 ID
     * @param {Object} params - 查询参数
     * @param {string} params.level - 日志级别（可选）
     * @param {number} params.limit - 每页数量（默认100）
     * @param {number} params.offset - 偏移量（默认0）
     */
    async getByTaskId(taskId, params = {}) {
        const response = await axios.get(`${API_BASE}/tasks/${taskId}/logs`, {params})
        return response.data
    },

    /**
     * 创建日志
     * @param {Object} log - 日志数据
     * @param {number} log.task_id - 任务 ID
     * @param {string} log.level - 日志级别
     * @param {string} log.message - 日志消息
     */
    async create(log) {
        const response = await axios.post(`${API_BASE}/logs`, log)
        return response.data
    },

    /**
     * 删除日志
     * @param {number} id - 日志 ID
     */
    async delete(id) {
        await axios.delete(`${API_BASE}/logs/${id}`)
    },

    /**
     * 删除任务的所有日志
     * @param {number} taskId - 任务 ID
     */
    async deleteByTaskId(taskId) {
        await axios.delete(`${API_BASE}/tasks/${taskId}/logs`)
    },

    /**
     * 删除所有日志
     * ⚠️ 警告：此操作将删除系统中的所有日志，不可恢复！
     */
    async deleteAll() {
        await axios.delete(`${API_BASE}/logs`)
    }
}