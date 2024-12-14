from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Room, DetailedList, Scheduler, ServiceQueue, WaitQueue, AirConditioner
import random
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
    for i in range(1, 6):
        serviceObject = serviceQueue.getServiceObject(i)
        if serviceObject:
            print(f"服务对象：{serviceObject}")
    waitQueue = WaitQueue()
    for i in range(1, 6):
        waitObject = waitQueue.getWaitObject(i)
        if waitObject:
            print(f"等待对象：{waitObject}")
def TestAirConditioner():
    list=[]
    for i in range(1, 6):
        airConditioner=AirConditioner.findAirConditioner(i)
        if airConditioner:
            list.append(i)
    print("空调列表：")
    print(list)
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
            Mode = "制冷"
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
    return addCorsHeaders(JsonResponse({'status': 'success'}))


