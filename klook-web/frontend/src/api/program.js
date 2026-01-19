import axios from 'axios'

const API_BASE = '/api'

/**
 * 优惠券项目管理 API
 */
export const programApi = {
    /**
     * 获取所有优惠券项目列表
     */
    async getAll() {
        const response = await axios.get(`${API_BASE}/programs`)
        return response.data
    },

    /**
     * 根据 ID 获取优惠券项目
     */
    async getById(id) {
        const response = await axios.get(`${API_BASE}/programs/${id}`)
        return response.data
    },

    /**
     * 创建优惠券项目
     */
    async create(program) {
        const response = await axios.post(`${API_BASE}/programs`, program)
        return response.data
    },

    /**
     * 更新优惠券项目
     */
    async update(id, program) {
        const response = await axios.put(`${API_BASE}/programs/${id}`, program)
        return response.data
    },

    /**
     * 删除优惠券项目
     */
    async delete(id) {
        await axios.delete(`${API_BASE}/programs/${id}`)
    }
}