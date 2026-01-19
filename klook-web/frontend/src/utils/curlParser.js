/**
 * 解析 curl 命令，提取 headers
 * @param {string} curlCommand - curl 命令字符串
 * @returns {Object} 包含 url 和 headers 的对象
 */
export function parseCurlCommand(curlCommand) {
    if (!curlCommand || typeof curlCommand !== 'string') {
        throw new Error('Invalid curl command')
    }

    // 移除换行符和多余的空格
    const cleanCommand = curlCommand
        .replace(/\\\n/g, ' ')  // 处理反斜杠换行
        .replace(/\n/g, ' ')    // 处理普通换行
        .replace(/\s+/g, ' ')   // 合并多个空格
        .trim()

    // 提取 URL
    let url = ''
    const urlMatch = cleanCommand.match(/curl\s+['"]?([^'">\s]+)['"]?/)
    if (urlMatch) {
        url = urlMatch[1]
    }

    // 提取所有的 -H 参数
    const headers = {}

    // 正则匹配 -H 'key: value' 或 -H "key: value" 或 -H 'key;' (无值的情况)
    const headerRegex = /-H\s+(['"])([^'"]+)\1/g
    let match

    while ((match = headerRegex.exec(cleanCommand)) !== null) {
        const headerString = match[2]

        // 解析 header，支持 "key: value" 和 "key;" 两种格式
        if (headerString.includes(':')) {
            const colonIndex = headerString.indexOf(':')
            const key = headerString.substring(0, colonIndex).trim()
            const value = headerString.substring(colonIndex + 1).trim()

            // 只保留有实际值的 header，跳过空值和以 ; 结尾的 header
            if (value && value !== ';' && !key.endsWith(';')) {
                headers[key] = value
            }
        } else if (headerString.endsWith(';')) {
            // 对于 "key;" 这种格式，跳过（通常是占位符）
            continue
        } else {
            // 其他情况，尝试提取键值
            const parts = headerString.split(/\s+/)
            if (parts.length >= 2) {
                headers[parts[0]] = parts.slice(1).join(' ')
            }
        }
    }

    // 提取 Cookie 参数 (-b 或 --cookie)
    // 匹配 -b 'cookie' 或 --cookie 'cookie' 或 -b "cookie" 或 --cookie "cookie"
    const cookieRegex = /(?:-b|--cookie)\s+(['"])([^'"]+)\1/g
    let cookieMatch
    const cookies = []

    while ((cookieMatch = cookieRegex.exec(cleanCommand)) !== null) {
        const cookieString = cookieMatch[2]
        cookies.push(cookieString)
    }

    // 如果找到了 cookie，添加到 headers
    if (cookies.length > 0) {
        // 合并所有 cookie（如果有多个 -b 参数）
        const cookieValue = cookies.join('; ')
        // 如果已经有 Cookie header，合并；否则直接添加
        if (headers['Cookie']) {
            headers['Cookie'] = headers['Cookie'] + '; ' + cookieValue
        } else {
            headers['Cookie'] = cookieValue
        }
    }

    return {
        url,
        headers
    }
}

/**
 * 验证解析结果
 * @param {Object} parsed - 解析结果
 * @returns {Object} 验证结果 { valid: boolean, message: string }
 */
export function validateParsedCurl(parsed) {
    if (!parsed.headers || Object.keys(parsed.headers).length === 0) {
        return {
            valid: false,
            message: '未能解析出任何 header，请检查 curl 命令格式'
        }
    }

    // 检查是否包含必要的 Klook headers
    const hasKlookHeaders = Object.keys(parsed.headers).some(key =>
        key.toLowerCase().includes('klook')
    )

    if (!hasKlookHeaders) {
        return {
            valid: false,
            message: '未找到 Klook 相关的 headers，请确认 curl 命令来自 Klook 网站'
        }
    }

    return {
        valid: true,
        message: `成功解析 ${Object.keys(parsed.headers).length} 个 headers`
    }
}

/**
 * 格式化 headers 为 JSON 字符串（美化）
 * @param {Object} headers - headers 对象
 * @returns {string} 格式化后的 JSON 字符串
 */
export function formatHeaders(headers) {
    return JSON.stringify(headers, null, 2)
}
