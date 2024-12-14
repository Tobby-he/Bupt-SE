from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Room, DetailedList, Scheduler, ServiceQueue, WaitQueue, AirConditioner, Receptionist, Customer, AccommodationOrder
import random
from django.apps import AppConfig

def initialize_rooms():
    """初始化创建5个房间"""
    if not Room.RoomList:  # 如果房间列表为空
        Mode = "制热"  # 默认制冷模式
        for _ in range(5):  # 创建5个房间
            Room.createRoom(Mode)
        print("初始化完成：创建了5个房间")
        print("房间列表：", [room.roomId for room in Room.RoomList])

# 在views.py开头调用初始化函数
initialize_rooms()

scheduler = Scheduler()

def CreateFiveRoom(Mode):
    if not Room.RoomList:
        room1 = Room.createRoom(Mode)
        room2 = Room.createRoom(Mode)
        room3 = Room.createRoom(Mode)
        room4 = Room.createRoom(Mode)
        room5 = Room.createRoom(Mode)
        print(room1.roomId, room2.roomId, room3.roomId, room4.roomId, room5.roomId)
def TestQueue():
    serviceQueue = ServiceQueue()
    for i in range(101, 104):
        serviceObject = serviceQueue.getServiceObject(i)
        if serviceObject:
            print(f"服务对象：{serviceObject}")
    waitQueue = WaitQueue()
    for i in range(101, 103):
        waitObject = waitQueue.getWaitObject(i)
        if waitObject:
            print(f"等待对象：{waitObject}")
def TestAirConditioner():
    list=[]
    for i in range(101, 106):
        airConditioner=AirConditioner.findAirConditioner(i)
        if airConditioner:
            list.append(i)
    print("空调列表：")
    print(list)
def TestTemperature():
    List = []
    for i in range(101, 106):
        temp=Room.getCurrentTemp(i)
        List.append(temp)
    print("温度列表：")
    print(List)
def addCorsHeaders(response):
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def handleTemperature(request):
    if request.method == "OPTIONS":
        return addCorsHeaders(JsonResponse({'status': 'ok'}))

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            newTemp = data.get('targetTemp')
            room_id = data.get('room_id')
            scheduler.changeTemp(room_id, newTemp)

            return addCorsHeaders(JsonResponse({'status': 'success'}))
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def handle_power(request):
    """处理开关机请求"""
    if request.method == "OPTIONS":
        return addCorsHeaders(JsonResponse({'status': 'ok'}))

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            power_status = data.get('isOn')
            room_id = data.get('room_id')
            # 输出 room_id 的类型
            print(f"room_id 的值: {room_id}, 类型: {type(room_id)}")
            Mode = "制热"
            print(f"收到房间{room_id}的开关机请求，当前状态：{'开' if power_status else '关'}")
            CreateFiveRoom(Mode)
            if power_status:
                Mode = "开机"
                scheduler.schedule(room_id, 2, Mode)  # 修改这里
            else:
                # 关机操作
                AirConditioner.powerOff(room_id)
                print(f"收到房间{room_id}的关机请求")
            return addCorsHeaders(JsonResponse({'status': 'success'}))
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)

@csrf_exempt
def get_rooms_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            room_id = data.get('room_id')
            # 查询数据库获取对应房间信息
            room = Room.getRoom(room_id)
            if not room:
                return JsonResponse({"status": "error", "message": f"房间 {room_id} 不存在"}, status=404)
            print(f"{room_id}！！！！！")
            print(f"{room.currentTemp}！！！！！!!!!!!!!!!!!!!!!!!!!!!!!!!")
            TestAirConditioner()

            ac = AirConditioner.findAirConditioner(room_id)  # 查询单个房间

            if ac is None:
              print(f"{room_id}没有空调")
            if_isOn = None if ac is None else True
           # if not ac:
               # return JsonResponse({"status": "error", "message": f"空调 {room_id} 不存在"}, status=404)
            # 模拟返回房间状态
            room_status = {
                "roomId": room.roomId,
                "currentTemp": room.currentTemp,
                "isOn1": if_isOn,
                #"fanSpeed": ac.fanSpeed,
            }
            if ac:
                room_status["fanSpeed"] = ac.fanSpeed
                room_status["targetTemp"] = ac.targetTemp
            return JsonResponse({"status": "success", "data": room_status})
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "无效的JSON数据"}, status=400)
    return JsonResponse({"status": "error", "message": "只支持POST请求"}, status=405)
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def handle_fan_speed(request):
    """处理风速调节请求"""
    if request.method == "OPTIONS":
        return addCorsHeaders(JsonResponse({'status': 'ok'}))
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            speed = data.get('fanSpeed')
            room_id = data.get('room_id')
            print(f"收到调节风速请求，目标风速：{speed}")
            # 调用调度器的风速调节方法
            Mode = "调风"
            scheduler.schedule(room_id, speed, Mode)  # 修改这里
            return addCorsHeaders(JsonResponse({'status': 'success'}))
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的JSON数据'}, status=400)
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def Test(request):
    TestAirConditioner()
    TestQueue()
    TestTemperature()
    return addCorsHeaders(JsonResponse({'status': 'success'}))

@csrf_exempt
@require_http_methods(["POST"])
def register_customer(request):
    """处理顾客注册请求"""
    try:
        data = json.loads(request.body)
        cust_id = data.get('cust_id')
        cust_name = data.get('cust_name')
        phone_number = data.get('number')
        check_in_date = data.get('date')
        
        # 验证必填字段
        if not all([cust_id, cust_name, phone_number, check_in_date]):
            return JsonResponse({
                'status': 'error',
                'message': '请填写所有必填字段'
            })
        
        # 注册顾客
        receptionist = Receptionist()
        success = receptionist.registerCustomer(cust_id, cust_name, phone_number, check_in_date)
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': '顾客注册成功'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': '顾客ID已存在'
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def check_room_state(request):
    """处理查询房间状态请求"""
    try:
        data = json.loads(request.body)
        date = data.get('date')
        
        if not date:
            return JsonResponse({
                'status': 'error',
                'message': '请提供查询日期'
            })
        
        # 查询房间状态
        receptionist = Receptionist()
        room_states = receptionist.checkRoomState(date)
        
        return JsonResponse({
            'status': 'success',
            'room_states': room_states
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def create_accommodation_order(request):
    """处理创建住宿订单请求"""
    try:
        data = json.loads(request.body)
        customer_id = data.get('customer_id')
        room_id = data.get('room_id')
        
        if not all([customer_id, room_id]):
            return JsonResponse({
                'status': 'error',
                'message': '请提供顾客ID和房间号'
            })
        
        # 创建订单
        receptionist = Receptionist()
        success = receptionist.createAccommodationOrder(customer_id, room_id)
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': '订单创建成功'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': '创建订单失败，请检查房间是否已被占用或顾客ID是否存在'
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def verify_customer(request):
    """验证顾客身份"""
    if request.method == "OPTIONS":
        return addCorsHeaders(JsonResponse({'status': 'ok'}))
        
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        customer_id = data.get('customer_id')
        
        print(f"验证请求 - 房间号: {room_id}, 顾客ID: {customer_id}")
        
        if not all([room_id, customer_id]):
            return addCorsHeaders(JsonResponse({
                'status': 'error',
                'message': '请提供房间号和顾客ID'
            }))
        
        # 查找房间
        room = Room.getRoom(room_id)
        if not room:
            print(f"未找到房间 {room_id}")
            return addCorsHeaders(JsonResponse({
                'status': 'error',
                'message': '未找到该房间'
            }))
            
        # 检查房间是否被占用
        if not room.isOccupied:
            print(f"房间 {room_id} 未被占用")
            return addCorsHeaders(JsonResponse({
                'status': 'error',
                'message': '该房间未被入住'
            }))
            
        # 验证顾客ID
        if str(room.currentCustomerId) != str(customer_id):
            print(f"顾客ID不匹配 - 期望: {room.currentCustomerId}, 实际: {customer_id}")
            return addCorsHeaders(JsonResponse({
                'status': 'error',
                'message': '顾客ID验证失败'
            }))
            
        print(f"验证成功 - 房间: {room_id}, 顾客: {customer_id}")
        return addCorsHeaders(JsonResponse({
            'status': 'success',
            'message': '验证成功'
        }))
        
    except Exception as e:
        print(f"验证过程发生错误: {str(e)}")
        return addCorsHeaders(JsonResponse({
            'status': 'error',
            'message': str(e)
        }))

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def process_checkout(request):
    """处理结账请求"""
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        
        # 调用结账处理
        checkout_details = AccommodationOrder.checkout(room_id)
        
        if checkout_details:
            return addCorsHeaders(JsonResponse({
                'status': 'success',
                'data': checkout_details
            }))
        else:
            return addCorsHeaders(JsonResponse({
                'status': 'error',
                'message': '结账失败，请检查房间状态'
            }))
    except Exception as e:
        print(f"结账处理错误: {str(e)}")
        return addCorsHeaders(JsonResponse({
            'status': 'error',
            'message': str(e)
        }))

@csrf_exempt
@csrf_exempt
def get_rooms_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            room_id = data.get('room_id')
            # 查询数据库获取对应房间信息
            room = Room.getRoom(room_id)
            if not room:
                return JsonResponse({"status": "error", "message": f"房间 {room_id} 不存在"}, status=404)
            print(f"{room_id}！！！！！")
            print(f"{room.currentTemp}！！！！！!!!!!!!!!!!!!!!!!!!!!!!!!!")
            TestAirConditioner()

            ac = AirConditioner.findAirConditioner(room_id)  # 查询单个房间

            if ac is None:
              print(f"{room_id}没有空调")
            if_isOn = None if ac is None else True
           # if not ac:
               # return JsonResponse({"status": "error", "message": f"空调 {room_id} 不存在"}, status=404)
            # 模拟返回房间状态
            room_status = {
                "roomId": room.roomId,
                "currentTemp": room.currentTemp,
                "isOn1": if_isOn,
                #"fanSpeed": ac.fanSpeed,
            }
            if ac:
                room_status["fanSpeed"] = ac.fanSpeed
                room_status["targetTemp"] = ac.targetTemp
            return JsonResponse({"status": "success", "data": room_status})
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "无效的JSON数据"}, status=400)
    return JsonResponse({"status": "error", "message": "只支持POST请求"}, status=405)

@csrf_exempt
@require_http_methods(["POST"])
def get_ac_status(request):
    """获取空调状态"""
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        
        if not room_id:
            return JsonResponse({
                'status': 'error',
                'message': '请提供房间号'
            })
            
        room = Room.getRoom(room_id)
        if not room:
            return JsonResponse({
                'status': 'error',
                'message': '未找到房间'
            })
            
        # 获取空调对象
        ac = AirConditioner.findAirConditioner(room_id)
        
        # 返回空调状态
        response_data = {
            'status': 'success',
            'data': {
                'is_on': ac is not None,
                'current_temp': room.currentTemp,
                'target_temp': ac.targetTemp if ac else None,
                'fan_speed': ac.fanSpeed if ac else None,
                'mode': ac.mode if ac else None,
                'total_temp_change': room.total_temp_change
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"获取空调状态时发生错误: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

