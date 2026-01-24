# dvc_param 生成逻辑分析

## 概述
通过分析 eplus.jp 网站的 JavaScript 代码（主要是 `diveObj.js`），我们发现了 `dvc_param` 的正确生成方式。

## URL 结构
```
https://eplus.jp/sf/detail/4317710001-P0030001?P6=001&P1=0402&P59=1
                         ^^^^^^^^^^
                         detail_code (前10位)
```

## 参数提取逻辑

### 1. detail_code 提取
从 URL 路径 `/sf/detail/` 后提取前10位字符：
```
4317710001-P0030001 → 取前10位 → 4317710001
```

### 2. 参数分解
```
detail_code = "4317710001"
kogyo_code = detail_code[0:6]   # 兴行代码：431771
tour_code = detail_code[6:10]   # 巡演代码：0001
```

### 3. time_token 获取
从页面隐藏字段 `<input id="time_token">` 的 value 属性获取：
```html
<input type="hidden" id="time_token" value="06b37d224a31e0abd616c77faf47e6ec0400f1697d089b089bfdcae299081a48">
```

### 4. 画面ID
固定值：`"S4"`（字符串）

## dvc_param 构造

### JavaScript 原始代码（diveObj.js）
```javascript
function callApiAsyncFromServletForDiveObj_S4(){
    // 提取detail code
    var search = location.pathname;
    var start = search.indexOf("/sf/detail/") + "/sf/detail/".length;
    var end = start + 10;
    var detail_codes = search.substring(start, end);  // "4317710001"

    // 获取time_token
    time_token = document.getElementById("time_token").value;

    // 画面ID
    urlParams["id"] = "S4";

    // 提取兴行代码和巡演代码
    kogyo_code = detail_codes.substring(0, 6);    // "431771"
    tour_code = detail_codes.substring(6, 10);    // "0001"

    // 构造参数（注意：这是逗号分隔的字符串，不是JSON对象）
    param[0] = time_token + ",S4," + kogyo_code + "," + tour_code;

    // 转换为JSON字符串
    allUrlParams["params"] = JSON.stringify(param);

    // 发送请求
    $.ajax({
        type: "GET",
        url: "/sf/dvcjudge",
        data: allUrlParams
    }).done(function (uniqueId) {
        // 设置Cookie
        Cookies.set("DVC_UNIQUE_ID", uniqueId, {path:'/', expires:date, domain:'.eplus.jp'});
    });
}
```

### Python 实现
```python
# 提取detail_code
detail_code = detail.split('?')[0].split('-')[0]  # "4317710001"
kogyo_code = detail_code[:6]   # "431771"
tour_code = detail_code[6:10]  # "0001"

# 构造dvc_param
dvc_param = json.dumps({
    "0": f"{time_token},S4,{kogyo_code},{tour_code}"
})

# 示例结果
# {"0":"06b37d224a31e0abd616c77faf47e6ec0400f1697d089b089bfdcae299081a48,S4,431771,0001"}
```

## API 调用

### 请求
```
GET https://eplus.jp/sf/dvcjudge?params=%7B%220%22%3A%2206b37d...081a48%2CS4%2C431771%2C0001%22%7D
```

URL解码后：
```
GET https://eplus.jp/sf/dvcjudge?params={"0":"06b37d224a31e0abd616c77faf47e6ec0400f1697d089b089bfdcae299081a48,S4,431771,0001"}
```

### 响应
返回 DVC_UNIQUE_ID（UUID格式）：
```
da6c2555-aeb5-4c45-b152-4bc7dc232a6c
```

## 常见错误

### ❌ 错误的构造方式（原VB.NET代码）
```vb
Dim DvcParam = $'[{{"0":"{TimeToken}",{S4},{Detail.Substring(0, 6)},{Detail.Substring(6, 4)}}}]'
```

问题：
1. 使用数组包裹对象 `[{...}]` 而不是直接对象 `{...}`
2. S4 作为变量而不是字符串 `"S4"`
3. 参数应该是逗号分隔的字符串，不是JSON对象的多个属性

### ✅ 正确的构造方式
```python
dvc_param = json.dumps({"0": f"{time_token},S4,{kogyo_code},{tour_code}"})
```

## 完整流程

1. **访问详情页**：`https://eplus.jp/sf/detail/4317710001-P0030001?P6=001&P1=0402&P59=1`
2. **解析HTML**：提取 `time_token` 和 `main_jsp1` URL
3. **构造dvc_param**：按照上述规则生成参数
4. **调用API**：`GET /sf/dvcjudge?params={dvc_param}`
5. **获取DVC_UNIQUE_ID**：从响应中获取UUID
6. **设置Cookie**：将 DVC_UNIQUE_ID 设置为Cookie
7. **访问主页面**：使用Cookie访问 `main_jsp1` URL

## 验证

通过Chrome DevTools Network面板可以看到实际的请求：
```
Request URL: https://eplus.jp/sf/dvcjudge?params=%7B%220%22%3A%2206b37d224a31e0abd616c77faf47e6ec0400f1697d089b089bfdcae299081a48%2CS4%2C431771%2C0001%22%7D
Status: 200
Response: da6c2555-aeb5-4c45-b152-4bc7dc232a6c
```
