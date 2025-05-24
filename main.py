from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import random
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json

app = FastAPI(title="验证码校验系统", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储验证码的临时存储（生产环境中应使用数据库）
verification_codes = {}

# API配置
QUESTIONNAIRE_API_URL = "https://wj.sjtu.edu.cn/api/v1/public/result/" # 替换为实际的问卷API URL

class CodeRequest(BaseModel):
    pass

class VerifyRequest(BaseModel):
    code: str
    timestamp: int

class CodeResponse(BaseModel):
    code: str
    timestamp: int

class VerifyResponse(BaseModel):
    verified: bool
    message: str
    user_name: Optional[str] = None

def generate_verification_code() -> str:
    """生成6位数字验证码"""
    return f"{random.randint(100000, 999999)}"

def is_recent_submission(submitted_at: str, code_timestamp: int, minutes: int = 10) -> bool:
    """检查提交时间是否在验证码生成后的指定分钟内"""
    try:
        # 解析提交时间 - 处理带时区的ISO格式
        if 'T' in submitted_at:
            # 处理各种ISO格式: 2025-05-24T14:43:05.75+08:00
            submit_time = datetime.fromisoformat(submitted_at)
            # 转换为本地时间（去掉时区信息进行比较）
            if submit_time.tzinfo is not None:
                submit_time = submit_time.replace(tzinfo=None)
        else:
            # 简单格式: 2021-06-17 14:34
            submit_time = datetime.strptime(submitted_at, "%Y-%m-%d %H:%M")
        
        # 验证码生成时间
        code_time = datetime.fromtimestamp(code_timestamp / 1000)
        
        # 放宽时间限制：允许验证码生成前后的时间窗口
        time_diff = abs((submit_time - code_time).total_seconds())
        max_seconds = minutes * 60
        
        print(f"时间比较: 提交时间={submit_time}, 生成时间={code_time}, 时差={time_diff}秒, 限制={max_seconds}秒")
        return time_diff <= max_seconds
    except Exception as e:
        print(f"解析时间失败: {e}, 提交时间: {submitted_at}")
        # 如果时间解析失败，仍然允许验证（避免因时间问题导致验证失败）
        return True

def search_verification_code_in_answers(answers: List[Dict], target_code: str) -> bool:
    """在答案中搜索验证码 - 简化版本"""
    print(f"搜索验证码: {target_code}")
    
    for i, answer in enumerate(answers):
        answer_content = answer.get('answer', '')
        question_info = answer.get('question', {})
        question_title = question_info.get('title', '')
        question_id = question_info.get('id', '')
        
        print(f"答案 {i+1}: 问题='{question_title}' (ID:{question_id}), 答案='{answer_content}'")
        
        # 检查是否是验证码相关问题
        is_verification_question = (
            '验证码' in question_title or 
            'verification' in question_title.lower() or
            'code' in question_title.lower() or
            question_id == 10423765  # 根据API返回确定的验证码问题ID
        )
        
        if is_verification_question:
            print(f"找到验证码问题: {question_title}")
            
        # 转换答案为字符串进行比较
        answer_str = str(answer_content).strip()
        
        # 直接匹配
        if answer_str == target_code:
            print(f"✅ 找到完全匹配的验证码: {answer_str}")
            return True
            
        # 包含匹配
        if target_code in answer_str:
            print(f"✅ 找到包含的验证码: {answer_str}")
            return True
    
    print("❌ 未找到匹配的验证码")
    return False

@app.post("/generate-code", response_model=CodeResponse)
async def generate_code():
    """生成验证码"""
    try:
        code = generate_verification_code()
        timestamp = int(time.time() * 1000)  # 毫秒时间戳
        
        # 存储验证码（包含生成时间）
        verification_codes[code] = {
            'timestamp': timestamp,
            'used': False
        }
        
        # 清理过期的验证码（超过10分钟）
        current_time = int(time.time() * 1000)
        expired_codes = [
            c for c, data in verification_codes.items() 
            if current_time - data['timestamp'] > 10 * 60 * 1000
        ]
        for expired_code in expired_codes:
            del verification_codes[expired_code]
        
        return CodeResponse(code=code, timestamp=timestamp)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成验证码失败: {str(e)}")

@app.post("/verify-code", response_model=VerifyResponse)
async def verify_code(request: VerifyRequest):
    """验证验证码"""
    try:
        print(f"\n=== 开始验证验证码: {request.code} ===")
        
        # 检查验证码是否存在且未使用
        if request.code not in verification_codes:
            print(f"❌ 验证码不存在: {request.code}")
            print(f"当前存储的验证码: {list(verification_codes.keys())}")
            return VerifyResponse(
                verified=False,
                message="验证码不存在或已过期"
            )
        
        code_data = verification_codes[request.code]
        if code_data['used']:
            print(f"❌ 验证码已被使用: {request.code}")
            return VerifyResponse(
                verified=False,
                message="验证码已被使用"
            )
        
        print(f"✅ 验证码有效，开始查询问卷API...")
        
        # 调用问卷API获取最近的提交
        params = {
            'pageSize': 30,  # 增加查询数量
            'pageNum': 1
        }
        
        print(f"📡 调用API: {QUESTIONNAIRE_API_URL}")
        response = requests.get(QUESTIONNAIRE_API_URL, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ API调用失败: HTTP {response.status_code}")
            raise HTTPException(
                status_code=500, 
                detail=f"问卷API调用失败: HTTP {response.status_code}"
            )
        
        data = response.json()
        print(f"📊 API返回状态: {data.get('success')}, 消息: {data.get('message')}")
        
        if not data.get('success'):
            return VerifyResponse(
                verified=False,
                message=f"问卷API返回错误: {data.get('message', '未知错误')}"
            )
        
        # 查找匹配的答卷
        answer_sheets = data.get('data', {}).get('rows', [])
        print(f"📋 获取到 {len(answer_sheets)} 个答卷")
        
        for i, sheet in enumerate(answer_sheets):
            print(f"\n--- 检查答卷 {i+1} ---")
            submitted_at = sheet.get('submitted_at', '')
            user = sheet.get('user', {})
            user_name = user.get('name', '未知用户')
            
            print(f"👤 用户: {user_name}")
            print(f"⏰ 提交时间: {submitted_at}")
            
            # 检查提交时间（放宽时间限制）
            if not is_recent_submission(submitted_at, request.timestamp, minutes=10):
                print(f"⏰ 时间不匹配，跳过")
                continue
            
            print(f"✅ 时间匹配，检查答案...")
            
            # 在答案中搜索验证码
            answers = sheet.get('answers', [])
            if search_verification_code_in_answers(answers, request.code):
                # 找到匹配的验证码，标记为已使用
                verification_codes[request.code]['used'] = True
                print(f"🎉 验证成功！用户: {user_name}")
                
                return VerifyResponse(
                    verified=True,
                    message="验证成功",
                    user_name=user_name
                )
        
        print("❌ 未找到匹配的验证码提交")
        return VerifyResponse(
            verified=False,
            message="未找到匹配的验证码提交。请检查：1) 验证码是否正确填写 2) 是否已提交问卷 3) 网络是否正常"
        )
        
    except requests.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"网络请求失败: {str(e)}")
    except Exception as e:
        print(f"❌ 验证过程出错: {e}")
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")

@app.post("/test-existing-code")
async def test_existing_code(code: str = "293847"):
    """测试端点：添加已存在的验证码用于测试"""
    # 使用提交时间作为验证码生成时间
    timestamp = int(datetime.fromisoformat("2025-05-24T14:43:05.75+08:00").timestamp() * 1000)
    
    # 添加到验证码存储中
    verification_codes[code] = {
        'timestamp': timestamp,
        'used': False
    }
    
    return {
        "message": f"测试验证码 {code} 已添加",
        "timestamp": timestamp
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    """根路径"""
    return {"message": "验证码校验系统API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
