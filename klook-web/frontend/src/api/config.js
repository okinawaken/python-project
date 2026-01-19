import axios from 'axios'

const API_BASE = '/api'

/**
 * 配置管理 API
 */
export const configApi = {
    /**
     * 获取所有配置列表
     */
    async getAll() {
        const response = await axios.get(`${API_BASE}/configs`)
        return response.data
    },

    /**
     * 根据 ID 获取配置
     */
    async getById(id) {
        const response = await axios.get(`${API_BASE}/configs/${id}`)
        return response.data
    },

    /**
     * 创建配置
     */
    async create(config) {
        const response = await axios.post(`${API_BASE}/configs`, config)
        return response.data
    },

    /**
     * 更新配置
     */
    async update(id, config) {
        const response = await axios.put(`${API_BASE}/configs/${id}`, config)
        return response.data
    },

    /**
     * 删除配置
     */
    async delete(id) {
        await axios.delete(`${API_BASE}/configs/${id}`)
    },

    /**
     * 验证配置
     */
    async validate(id) {
        const response = await axios.post(`${API_BASE}/configs/${id}/validate`)
        return response.data
    }
}