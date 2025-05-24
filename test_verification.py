#!/usr/bin/env python3
"""
测试验证码验证功能
使用API中已有的验证码进行测试
"""

import requests
import json
import time

# 测试配置
BASE_URL = "http://localhost:8000"

def test_verification():
    print("=== 验证码校验系统测试 ===\n")
    
    # 从API获取最新提交的验证码
    print("1. 获取最新的问卷提交...")
    api_url = "https://wj.sjtu.edu.cn/api/v1/public/result/" # 替换为实际的问卷API URL
    
    try:
        response = requests.get(api_url)
        data = response.json()
        
        if data.get('success'):
            rows = data.get('data', {}).get('rows', [])
            if rows:
                # 获取最新的验证码
                latest_submission = rows[0]
                answers = latest_submission.get('answers', [])
                
                verification_code = None
                for answer in answers:
                    question = answer.get('question', {})
                    if '验证码' in question.get('title', ''):
                        verification_code = answer.get('answer', '')
                        break
                
                if verification_code:
                    print(f"找到最新验证码: {verification_code}")
                    submitted_at = latest_submission.get('submitted_at', '')
                    user_name = latest_submission.get('user', {}).get('name', '')
                    print(f"提交时间: {submitted_at}")
                    print(f"用户: {user_name}")
                    
                    # 测试验证
                    print(f"\n2. 测试验证码验证...")
                    
                    # 构造当前时间戳（模拟刚生成的验证码）
                    current_timestamp = int(time.time() * 1000)
                    
                    verify_data = {
                        "code": verification_code,
                        "timestamp": current_timestamp
                    }
                    
                    verify_response = requests.post(
                        f"{BASE_URL}/verify-code",
                        json=verify_data
                    )
                    
                    if verify_response.status_code == 200:
                        result = verify_response.json()
                        print(f"验证结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
                        
                        if result.get('verified'):
                            print("✅ 验证成功！")
                        else:
                            print("❌ 验证失败")
                            print(f"失败原因: {result.get('message')}")
                    else:
                        print(f"❌ 验证请求失败: HTTP {verify_response.status_code}")
                        print(verify_response.text)
                        
                else:
                    print("❌ 未找到验证码字段")
            else:
                print("❌ 没有找到问卷提交记录")
        else:
            print(f"❌ API调用失败: {data.get('message')}")
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")

if __name__ == "__main__":
    test_verification()
