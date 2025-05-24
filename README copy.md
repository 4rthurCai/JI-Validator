# 验证码校验系统

这是一个基于FastAPI后端和原生JavaScript前端的验证码校验系统。

## 功能特性

- 🎯 生成6位数字验证码并自动复制到剪贴板
- 🖥️ 自动打开问卷页面（新窗口模式）
- 🔍 实时验证用户提交的验证码
- ✅ 验证成功后显示用户姓名
- 🎨 现代化响应式UI设计

## 系统架构

### 前端 (index.html)
- 使用原生JavaScript，无需任何框架
- 现代化CSS样式，支持渐变背景和动画效果
- 自动复制验证码到剪贴板
- 使用`window.open`打开新窗口（非新标签页）

### 后端 (main.py)
- FastAPI框架，提供RESTful API
- 支持CORS跨域请求
- 自动调用问卷API验证提交
- 智能匹配验证码和用户提交

## 安装和运行

### 方法1: 使用启动脚本（推荐）

```bash
cd verification-system
./start.sh
```

### 方法2: 手动安装

1. 安装Python依赖：
```bash
pip install -r requirements.txt
```

2. 启动后端服务：
```bash
python main.py
```
或
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

3. 打开前端页面：
直接在浏览器中打开 `index.html` 文件

## 使用流程

1. **生成验证码**
   - 打开 `index.html` 页面
   - 点击"生成验证码"按钮
   - 验证码自动复制到剪贴板并显示在页面上

2. **填写问卷**
   - 系统自动打开问卷页面（新窗口）
   - 在问卷中粘贴验证码
   - 提交问卷

3. **验证结果**
   - 返回验证系统页面
   - 点击"验证提交"按钮
   - 系统自动验证并显示结果

## API接口

### POST /generate-code
生成新的验证码

**响应示例：**
```json
{
  "code": "123456",
  "timestamp": 1684567890000
}
```

### POST /verify-code
验证提交的验证码

**请求示例：**
```json
{
  "code": "123456",
  "timestamp": 1684567890000
}
```

**响应示例：**
```json
{
  "verified": true,
  "message": "验证成功",
  "user_name": "张三"
}
```

### GET /health
健康检查接口

## 配置说明

### 验证逻辑
- 验证码有效期：10分钟
- 查询范围：最近20个提交
- 时间窗口：验证码生成后5分钟内的提交

## 安全特性

- 验证码一次性使用（使用后自动失效）
- 时间戳验证防止重放攻击
- 自动清理过期验证码
- CORS配置（生产环境需要限制域名）

## 技术栈

### 前端
- HTML5
- CSS3 (Flexbox, Grid, 动画)
- 原生JavaScript (ES6+)
- Clipboard API

### 后端
- Python 3.8+
- FastAPI
- Pydantic (数据验证)
- Requests (HTTP客户端)
- Uvicorn (ASGI服务器)

## 浏览器支持

- Chrome 66+ (推荐)
- Firefox 63+
- Safari 13.1+
- Edge 79+

## 注意事项

1. **弹窗拦截**: 某些浏览器可能拦截新窗口，请允许弹窗
2. **HTTPS**: 剪贴板API在HTTPS环境下工作最佳
3. **CORS**: 生产环境需要配置正确的CORS域名
4. **时区**: 系统使用本地时区进行时间比较

## 故障排除

### 常见问题

1. **验证码复制失败**
   - 检查浏览器是否支持Clipboard API
   - 尝试手动选择验证码文本

2. **新窗口打开失败**
   - 检查浏览器弹窗拦截设置
   - 手动打开问卷链接

3. **验证失败**
   - 确认验证码正确粘贴到问卷中
   - 检查网络连接
   - 确认在时间窗口内提交

4. **API连接失败**
   - 检查后端服务是否正常运行
   - 确认端口8000未被占用
   - 检查防火墙设置

## 开发和扩展

### 添加新功能
- 修改 `main.py` 添加新的API端点
- 修改 `index.html` 添加新的前端功能

### 数据库集成
生产环境建议将验证码存储替换为数据库：
```python
# 替换内存存储
verification_codes = {}

# 使用数据库（如Redis, PostgreSQL等）
```

### 部署建议
- 使用Docker容器化部署
- 配置反向代理（Nginx）
- 启用HTTPS
- 设置环境变量管理配置

## 许可证

MIT License
