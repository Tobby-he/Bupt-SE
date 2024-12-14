import requests
import json
import time

SERVER_URL = "http://127.0.0.1:8000/api/"

def send_request(endpoint, method="POST", data=None):
    """发送请求到服务器"""
    url = f"{SERVER_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def get_room_status(room_id):
    """获取房间状态"""
    response = send_request("room_status/", data={"room_id": room_id})
    if response and response.get('status') == 'success':
        return response.get('data', {})
    return None

def test_ac_fee():
    """测试空调计费功能"""
    room_id = 104
    customer_id = "test010"
    
    # 1. 注册顾客
    print("\n1. 注册顾客...")
    customer_data = {
        "cust_id": customer_id,
        "cust_name": "测试用户",
        "number": "13800138000",
        "date": time.strftime("%Y-%m-%dT%H:%M")
    }
    response = send_request("register-customer/", data=customer_data)
    print(f"注册结果: {response}")

    # 2. 创建入住订单
    print("\n2. 创建入住订单...")
    order_data = {
        "customer_id": customer_id,
        "room_id": room_id
    }
    response = send_request("create-accommodation-order/", data=order_data)
    print(f"入住结果: {response}")

    # 获取初始温度
    status = get_room_status(room_id)
    if status:
        print(f"\n初始房间温度: {status.get('current_temp', 'N/A')}°C")

    # 3. 开启空调
    print("\n3. 开启空调...")
    power_data = {
        "isOn": True,
        "room_id": room_id
    }
    response = send_request("power/", data=power_data)
    print(f"开启空调结果: {response}")
    
    # 4. 设置温度和风速，等待温度变化
    print("\n4. 设置温度和风速...")
    temp_data = {
        "targetTemp": 20,
        "room_id": room_id
    }
    response = send_request("temperature/", data=temp_data)
    print(f"设置温度结果: {response}")
    
    fan_data = {
        "fanSpeed": 2,  # 高风速
        "room_id": room_id
    }
    response = send_request("fan-speed/", data=fan_data)
    print(f"设置风速结果: {response}")
    
    # 5. 等待一段时间让温度变化，每10秒检查一次温度
    print("\n5. 监控温度变化（60秒）...")
    for i in range(6):
        time.sleep(10)
        status = get_room_status(room_id)
        if status:
            current_temp = status.get('current_temp', 'N/A')
            target_temp = status.get('target_temp', 'N/A')
            print(f"已等待 {(i+1)*10} 秒:")
            print(f"  当前温度: {current_temp}°C")
            print(f"  目标温度: {target_temp}°C")
            print(f"  累计温度变化: {status.get('total_temp_change', 'N/A')}°C")
            print(f"  空调状态: {status.get('ac_status', 'N/A')}")
            print("服务器返回的状态数据:", status)
    # 6. 结账查看费用
    print("\n6. 结账查看费用...")
    checkout_data = {
        "room_id": room_id
    }
    response = send_request("process-checkout/", data=checkout_data)
    if response and response.get('status') == 'success':
        details = response['data']
        print("\n结账详情:")
        print(f"顾客姓名: {details['customer_name']}")
        print(f"入住时间: {details['check_in_time']}")
        print(f"退房时间: {details['check_out_time']}")
        print(f"住宿天数: {details['days']}天")
        print(f"房间基础费用: ￥{details['base_fee_per_day']}/天")
        print(f"住宿费用: ￥{details['accommodation_fee']}")
        print(f"空调费用: ￥{details['ac_fee']}")
        print(f"总计费用: ￥{details['total_fee']}")
    else:
        print("结账失败")

if __name__ == "__main__":
    test_ac_fee() 