import requests
import json
import time

SERVER_URL = "http://127.0.0.1:8000/api/"  # Django 服务器地址

def send_request(action, data=None):
    """模拟 JS 函数 sendToServer，向后端发送请求"""
    endpoints = {
        "increaseTemp": "temperature/",
        "decreaseTemp": "temperature/",
        "togglePower": "power/",
        "changeFanSpeed": "fan-speed/",
        "test": "test/",
    }

    endpoint = endpoints.get(action)
    if not endpoint:
        print(f"Error: Unknown action '{action}'")
        return

    url = f"{SERVER_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    payload = {"action": action}
    if data:
        payload.update(data)

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # 抛出 HTTP 错误 (4xx 或 5xx)
        result = response.json()
        if result.get('status') == 'success':
            print(f"Request '{action}' successful.")
        else:
            print(f"Request '{action}' failed: {result}")
    except requests.exceptions.RequestException as e:
        print(f"Request '{action}' failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")

def main():
    # 定时操作序列
    send_request("togglePower", {"isOn": True, "room_id": 101})
    time.sleep(10)  # 第一分钟
    send_request("decreaseTemp", {"targetTemp": 18, "room_id": 101})
    time.sleep(0.1)
    send_request("togglePower", {"isOn": True, "room_id": 102})
    time.sleep(0.1)
    send_request("togglePower", {"isOn": True, "room_id": 105})
    time.sleep(9.8)  # 第二分钟
    send_request("togglePower", {"isOn": True, "room_id": 103})
    time.sleep(10)  # 第三分钟
    send_request("decreaseTemp", {"targetTemp": 19, "room_id": 102})
    time.sleep(0.1)
    send_request("togglePower", {"isOn": True, "room_id": 104})
    time.sleep(9.9)  # 第四分钟
    send_request("decreaseTemp", {"targetTemp": 22, "room_id": 105})
    time.sleep(10)  # 第五分钟
    send_request("changeFanSpeed", {"fanSpeed": 3, "room_id": 101})
    time.sleep(10)  # 第6分钟
    send_request("togglePower", {"isOn": False, "room_id": 102})
    time.sleep(10)  # 第7分钟
    send_request("togglePower", {"isOn": True, "room_id": 102})
    time.sleep(0.1)
    send_request("changeFanSpeed", {"fanSpeed": 3, "room_id": 105})
    time.sleep(9.9)  # 第8分钟
    time.sleep(10)  # 第9分钟
    send_request("decreaseTemp", {"targetTemp": 22, "room_id": 101})
    time.sleep(0.1)
    send_request("decreaseTemp", {"targetTemp": 18, "room_id": 104})
    time.sleep(0.1)
    send_request("changeFanSpeed", {"fanSpeed": 3, "room_id": 104})
    time.sleep(9.8)  # 第10分钟
    time.sleep(10)  # 第11分钟
    send_request("decreaseTemp", {"targetTemp": 22, "room_id": 102})
    time.sleep(10)  # 第12分钟
    send_request("changeFanSpeed", {"fanSpeed": 1, "room_id": 105})
    time.sleep(10)  # 第13分钟
    time.sleep(10)  # 第14分钟
    send_request("togglePower", {"isOn": False, "room_id": 101})
    time.sleep(0.1)
    send_request("decreaseTemp", {"targetTemp": 24, "room_id": 103})
    time.sleep(0.1)
    send_request("changeFanSpeed", {"fanSpeed": 1, "room_id": 103})
    time.sleep(9.8)  # 第15分钟
    send_request("decreaseTemp", {"targetTemp": 20, "room_id": 105})
    time.sleep(0.1)
    send_request("changeFanSpeed", {"fanSpeed": 3, "room_id": 105})
    time.sleep(9.9)  # 第16分钟
    send_request("togglePower", {"isOn": False, "room_id": 102})
    time.sleep(10)  # 第17分钟
    send_request("changeFanSpeed", {"fanSpeed": 3, "room_id": 103})
    time.sleep(10)  # 第18分钟
    send_request("togglePower", {"isOn": True, "room_id": 101})
    time.sleep(0.1)
    send_request("decreaseTemp", {"targetTemp": 20, "room_id": 104})
    time.sleep(0.1)
    send_request("changeFanSpeed", {"fanSpeed": 2, "room_id": 104})
    time.sleep(9.8)  # 第19分钟
    send_request("togglePower", {"isOn": True, "room_id": 102})
    time.sleep(10)  # 第20分钟
    send_request("decreaseTemp", {"targetTemp": 25, "room_id": 105})
    time.sleep(10)  # 第21分钟
    time.sleep(10)  # 第22分钟
    send_request("togglePower", {"isOn": False, "room_id": 103})
    time.sleep(10)  # 第23分钟
    send_request("togglePower", {"isOn": False, "room_id": 105})
    time.sleep(10)  # 第24分钟
    send_request("togglePower", {"isOn": False, "room_id": 101})
    time.sleep(10)  # 第25分钟
    send_request("togglePower", {"isOn": False, "room_id": 102})
    time.sleep(0.1)
    send_request("togglePower", {"isOn": False, "room_id": 104})
    send_request("test")


if __name__ == "__main__":
    main()