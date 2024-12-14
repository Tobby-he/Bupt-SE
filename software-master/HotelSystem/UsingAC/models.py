from django.db import models
from datetime import datetime,timedelta
import threading
import warnings
import math
import time
warnings.filterwarnings('ignore', category=RuntimeWarning)

# 房间类，表示酒店中的一个房间
class Room:
    # 将 RoomList 和 initTempList 变为类变量，所有实例共享
    RoomList = []
    initTempList1 = [32, 28, 30, 29, 35]  # 作为类变量定义
    initTempList2 = [10, 15, 18, 12, 14]  # 作为类变量定义
    
    @classmethod
    def getActualRoomId(cls, index):
        """将索引转换为实际房间号"""
        return 101 + index
    
    @classmethod
    def getListIndex(cls, roomId):
        """将实际房间号转换为列表索引"""
        return roomId - 101
    
    def __init__(self, roomId, initialTemp=None, currentTemp=None, Timer=None):
        self.roomId = roomId  # roomId 现在是 101-105
        self.initialTemp = initialTemp
        self.currentTemp = currentTemp
        self.Timer = None
        # 添加新的属性
        self.isOccupied = False  # 房间是否被占用
        self.currentCustomerId = None  # 当前入住的顾客ID
        self.checkInTime = None  # 入住时间
        self.checkOutTime = None  # 退房时间
        self.ac_fee = 0  # 添加空调费用属性
        self.last_fee_update = None  # 上次费用更新时间
        self.total_temp_change = 0  # 添加总温度变化量属性
    @classmethod
    def getInitialTemp(cls, roomId, Mode):
        index = cls.getListIndex(roomId)
        if index >= len(cls.initTempList1) or index < 0:
            print(f"房间号超出范围 - ID: {roomId}")
            return 0
        else:
            if Mode == "制冷":
                return cls.initTempList1[index]
            else:
                return cls.initTempList2[index]
    @classmethod
    def getCurrentTemp(cls, roomId):
        room = cls.getRoom(roomId)
        return room.currentTemp
    @classmethod
    def setCurrentTemp(cls, roomId, currentTemp):
        room = cls.getRoom(roomId)
        room.currentTemp = currentTemp
    @classmethod
    def createRoom(cls, Mode):
        """创建新房间"""
        # 获取新房间的ID
        newRoomId = cls.getActualRoomId(len(cls.RoomList))
        index = cls.getListIndex(newRoomId)
        
        if index >= len(cls.initTempList1):
            print(f"房间号超出范围 - ID: {newRoomId}")
            return None
        # 从初始温度列表中获取对应的温度
        if Mode == "制冷":
            initTemp = cls.initTempList1[index]
        else:
            initTemp = cls.initTempList2[index]
            
        # 创建新房间实例
        newRoom = Room(
            roomId=newRoomId,
            initialTemp=initTemp,
            currentTemp=initTemp,
            Timer=None
        )
        
        # 添加到房间列表
        cls.RoomList.append(newRoom)
        print(f"创建新房间 - ID: {newRoomId}, 初始温度: {initTemp}°C")
        return newRoom
    @classmethod
    def fiveRoomTimerStart(cls):
        room1 = Room.getRoom(101)
        if not room1.Timer:
            room2 = Room.getRoom(102)
            room3 = Room.getRoom(103)
            room4 = Room.getRoom(104)
            room5 = Room.getRoom(105)
            room1.Timer = RoomTimer(101)
            room1.Timer.startTimer()
            room2.Timer = RoomTimer(102)
            room2.Timer.startTimer()
            room3.Timer = RoomTimer(103)
            room3.Timer.startTimer()
            room4.Timer = RoomTimer(104)
            room4.Timer.startTimer()
            room5.Timer = RoomTimer(105)
            room5.Timer.startTimer()
    @classmethod  # 使用 @classmethod 代替 @staticmethod
    def destroyRoom(cls, roomId):
        """销毁指定房间"""
        # 查找并移除房间
        for room in cls.RoomList:
            if room.roomId == roomId:
                cls.RoomList.remove(room)
                print(f"销毁房间 - ID: {roomId}")
                return True
        print(f"未找到房间 - ID: {roomId}")
        return False
    @classmethod
    def getRoom(cls, roomId):
        try:
            roomId = int(roomId)  # 将 roomId 转换为整数类型
            if roomId < 101 or roomId > 105:
                print(f"房间号 {roomId} 超出有效范围(101-105)")
                return None
            
            for room in cls.RoomList:
                if room.roomId == roomId:
                    return room

            print(f"未找到房间 - ID: {roomId}")
            print(f"当前房间表: {[room.roomId for room in cls.RoomList]}")
            return None
        
        except ValueError:
            print(f"无效的房间 ID: {roomId}，无法转换为整数")
            return None
    @classmethod
    def returnDeathTemp(cls, roomId):
        room = cls.getRoom(roomId)
        # 分配一个服务计时器
        timer = returnTempTimer()
        room.Timer = timer
        timer.start()
    @classmethod
    def updateTemp(cls, roomId):
        ''' 
        这个函数10秒钟运行一次，目的是10秒更新一次房间的温度，因为房间有五个，所以会有五个updateTemp函数10秒运行一次
        '''
        # 先看有没有房间对应的空调对象
        airConditioner = AirConditioner.findAirConditioner(roomId)
        # 再找对应的房间对象
        room = Room.getRoom(roomId)
        # 如果有，看是否到达目标温度
        if airConditioner:
            if airConditioner.reachTemp == True:
                # 启动回温函数
                print(f"{roomId}开始回温，空调未关机")
                airConditioner.reachTempCount = airConditioner.reachTempCount + 1
                if airConditioner.mode == "制冷":
                    # 看温度是否大于房间初始温度
                    
                    if room.currentTemp < room.initialTemp:
                        room.currentTemp = room.currentTemp + 0.5
                    else:
                        room.currentTemp = room.initialTemp
                else:
                    # 看温度是否小于房间初始温度
                    if room.currentTemp > room.initialTemp:
                        room.currentTemp = room.currentTemp - 0.5
                    else:
                        room.currentTemp = room.initialTemp
                print(f"{roomId}回温后，当前温度：{room.currentTemp}°C")
                print(f"{roomId}回温次数：{airConditioner.reachTempCount}")
            else:
                # 如果未到达目标温度，则看是否在服务队列里
                if ServiceQueue.contains(roomId):
                    ''' 
                    在这个if下，第roomID个房间在服务队列里且风速为
                    airConditioner.fanSpeed
                    所以这时需要计费
                    在这里，你可以创一个详单，以及计算费用
                    因为是10秒运行一次这个函数，所以计算费用的思路应该是更新，而不是一口气算出来
                    比如，费用=费用+风速（这里省略了风速后面的1分钟系数，直接加的，可以看上面，温度计算也是这个逻辑）
                    '''

                    old_temp = room.currentTemp  # 记录之前的温度
                    room.currentTemp = airConditioner.calculateTemp(roomId)
                    # 计算温度变化量（取绝对值）
                    temp_change = abs(room.currentTemp - old_temp)
                    room.total_temp_change += temp_change
                    print(f"房间{roomId} 温度变化：{temp_change:.1f}度而且在服务队列里，累计变化：{room.total_temp_change:.1f}度")
                else:
                    # 什么都不做
                    a = 1
        else:
            print(f"{roomId}空调关机，开始回温")
            # 看房间的初始温度大于20还是小于20
            if room.initialTemp > 20:
                # 如果是制冷，那么再看当前温度是否大于初始温度  
                if room.currentTemp < room.initialTemp:
                    room.currentTemp = room.currentTemp + 0.5
                else:
                    room.currentTemp = room.initialTemp
            else:
                # 如果是制热，那么再看当前温度是否小于初始温度
                if room.currentTemp > room.initialTemp:
                    room.currentTemp = room.currentTemp - 0.5
                else:
                    room.currentTemp = room.initialTemp
            print(f"{roomId}回温后，当前温度：{room.currentTemp}°C")
    @classmethod
    def updateState(cls, roomId):
        # 先看有没有房间对应的空调对象
        airConditioner = AirConditioner.findAirConditioner(roomId)
        # 再找对应的房间对象
        room = Room.getRoom(roomId)
        # 如果有，看是否到达目标温度
        if airConditioner:
            if airConditioner.reachTemp == True:
                if airConditioner.reachTempCount == 0:
                    # 如果他在服务队列里
                    if ServiceQueue.contains(roomId):
                        ServiceQueue.removeRequest(roomId)
                        # 在等待队列里找一个等待计时器最小的并加入服务队列
                        roomId1 = WaitQueue.GetLeastTimeRoomId()
                        if roomId1:
                            waitobj= WaitQueue.getWaitObject(roomId1)
                            ServiceQueue.addServiceQueue(roomId1, waitobj["fanSpeed"])
                        else:
                            print(f"{roomId}到达目标温度，但是没有找到等待队列里的房间")
                    # 如果他在等待队列里
                    if WaitQueue.contains(roomId):
                        WaitQueue.removeRequest(roomId)
                    
                # 如果连续回温两次，则发送请求
                if airConditioner.reachTempCount == 2:
                    print(f"{roomId}连续回温两次，发送请求")
                    scheduler = Scheduler()
                    scheduler.schedule(roomId, airConditioner.fanSpeed, "调风")
                    airConditioner.reachTempCount = 0
                    airConditioner.reachTemp = False
                
            else:
                # 什么都不做
                a = 1


# 空调类，表示房间内的空调设备
class AirConditioner:
    # 将空调列表变为类变量
    airConditionerList = []

    def __init__(self, roomId, initTemp, mode, targetTemp=25.0, fanSpeed=2):
        self.roomId = roomId
        self.targetTemp = targetTemp
        self.fanSpeed = fanSpeed
        self.serviceTime = 0
        self.acId = roomId
        self.reachTemp = False
        self.reachTempCount = 0
        self.mode = mode
        self.truemode = mode
    @classmethod
    def getFanSpeed(cls, roomId):
        airConditioner = cls.findAirConditioner(roomId)
        return airConditioner.fanSpeed
    @classmethod
    def returnLiveTemp(cls, roomId):
        # 分配一个回温计时器
        timer = serviceTimer()
        timer.start()
    @classmethod
    def getAirConditioner(cls, roomId):
        """获取指定房间的空调实例"""
        return cls.airConditionerList.get(roomId)

    @classmethod
    def removeAirConditioner(cls, roomId):
        """移除指定房间的空调"""
        airConditioner = cls.findAirConditioner(roomId)
        if airConditioner:
            cls.airConditionerList.remove(airConditioner)
            print(f"移除房间 {roomId} 的空调")
    @classmethod
    def getTargetTemp(cls, roomId):
        airConditioner = cls.findAirConditioner(roomId)
        return airConditioner.targetTemp
    @classmethod
    def getMode(cls, roomId):
        airConditioner = cls.findAirConditioner(roomId)
        return airConditioner.mode
    @classmethod
    def setTargetTemp(cls, roomId, targetTemp):
        airConditioner = cls.findAirConditioner(roomId)
        if airConditioner.truemode == "制冷":
            if targetTemp > 28:
                airConditioner.targetTemp = 28
            if targetTemp < 18:
                airConditioner.targetTemp = 18
        if airConditioner.truemode == "制热":
            if targetTemp > 25:
                airConditioner.targetTemp = 25
            if targetTemp < 18:
                airConditioner.targetTemp = 18
        currentTemp = Room.getCurrentTemp(roomId)
        if currentTemp > targetTemp:
            airConditioner.mode = "制冷"
        if currentTemp < targetTemp:
            airConditioner.mode = "制热"
        print(f"设置目标温度：{targetTemp}°C")

    @classmethod
    def setFanSpeed(cls, roomId, fanSpeed):
        airConditioner = cls.findAirConditioner(roomId)
        airConditioner.fanSpeed = fanSpeed
        print(f"设置风速：{fanSpeed}")
    @classmethod
    def findAirConditioner(cls, roomId):
        for airConditioner in cls.airConditionerList:
            if airConditioner.roomId == roomId:
                return airConditioner
        return None
    @classmethod
    def powerOn(cls, room, AirConditionerMode):
        """开启空调"""
        # 设置目标温度
        if AirConditionerMode == "制冷":
            targetTemp = 18
        elif AirConditionerMode == "制热":
            targetTemp = 25
        else:
            print(f"无效的空调模式：{AirConditionerMode}")
            return None
        Room.fiveRoomTimerStart()
        roomId = room.roomId
        # 创建新的空调实例
        newAirConditioner = AirConditioner(
            roomId=roomId,
            targetTemp=targetTemp,
            fanSpeed=2,
            initTemp=room.initialTemp,
            mode=AirConditionerMode
        )
        newAirConditioner.acId = roomId  # acId 与 roomId 相同
        
        # 将新实例添加到列表中
        cls.airConditionerList.append(newAirConditioner)
        
        print(f"空调开启 - 房间号：{roomId}")
        print(f"空调ID：{roomId}")  # acId 与 roomId 相同
        print(f"模式：{AirConditionerMode}")
        print(f"目标温度：{targetTemp}°C")
        print(f"风速：2")
        
        return newAirConditioner
    @classmethod
    def powerOff(cls, roomId):
        # 关机的时候
        # 如果他在服务队列里
        if ServiceQueue.contains(roomId):
            ServiceQueue.removeRequest(roomId)
            # 在等待队列里找一个等待计时器最小的并加入服务队列
            roomId1 = WaitQueue.GetLeastTimeRoomId()
            if roomId1:
                waitobj= WaitQueue.getWaitObject(roomId1)
                ServiceQueue.addServiceQueue(roomId1, waitobj["fanSpeed"])
            else:
                print(f"{roomId}关机了，但是等待队列没有东西")
        # 如果等待队列非空，则直接移除
        if WaitQueue.getListLength() > 0:
            # 从等待队列里移除
            WaitQueue.removeRequest(roomId)
        # 然后找到空调实例，并清除
        airConditioner = cls.findAirConditioner(roomId)
        cls.removeAirConditioner(roomId)


    @classmethod
    def createDetailedList(self, startTime, endTime, mode):
        detailedList = DetailedList.objects.create(
            start_time=startTime,
            end_time=endTime,
            mode=mode,
            target_temp=self.targetTemp,
            fan_speed=self.fanSpeed,
            rate=0.5,
            fee=self.getCurrentFee(),
            room=self.room.id
        )
        return detailedList
    @classmethod
    def changeCurrentTemp(cls, roomId,currentTemp):
        airConditioner = cls.findAirConditioner(roomId)
        airConditioner.currentTemp = currentTemp
        print(f"改变房间{roomId}的当前温度为：{currentTemp}°C")
    @classmethod
    def getCurrentTemp(cls, roomId):
        airConditioner = cls.findAirConditioner(roomId)
        return airConditioner.currentTemp
    @classmethod
    def calculateTemp(cls, roomId):
        # duration 是分钟
        currentTemp = Room.getCurrentTemp(roomId)
        fanspeed = AirConditioner.getFanSpeed(roomId)
        targetTemp = AirConditioner.getTargetTemp(roomId)
        Mode = AirConditioner.getMode(roomId)
        airConditioner = cls.findAirConditioner(roomId)
        if fanspeed == 1:
            speed = 0.33
        elif fanspeed == 2:
            speed = 0.5
        else:
            speed = 1
        # 计算温度
        if Mode == "制冷":
            newTemp = currentTemp - speed
            if newTemp < targetTemp:
                newTemp = targetTemp
                airConditioner.reachTemp = True
                Room.setCurrentTemp(roomId, newTemp)
                print(f"房间{roomId}到达目标温度，当前温度：{newTemp}°C")
                return newTemp
        else:
            newTemp = currentTemp + speed
            if newTemp > targetTemp:
                newTemp = targetTemp
                airConditioner.reachTemp = True
                Room.setCurrentTemp(roomId, newTemp)
                print(f"房间{roomId}到达目标温度，当前温度：{newTemp}°C")
                return newTemp
        print(f"计算温度 - 房间号：{roomId}, 当前温度：{currentTemp}°C, 目标温度：{targetTemp}°C, 新温度：{newTemp}°C")
        return newTemp


# 详单类，记录每次空调服务的详情
class DetailedList(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)  # 服务开始时间
    end_time = models.DateTimeField(null=True)  # 服务结束时间
    target_temp = models.FloatField()  # 目标温度
    mode = models.CharField(max_length=20)  # 空调模式
    fan_speed = models.IntegerField()  # 风速
    rate = models.FloatField()  # 费率
    fee = models.FloatField()  # 费用
    room = models.IntegerField(default=1)  # 房间号

class ServiceQueue:
    # 将队列变为类变量
    serviceQueue = []

    @classmethod
    def addServiceQueue(cls, roomId, fanSpeed):
        """添加服务请求到服务队列"""
        serviceObj = {
            "roomId": roomId,
            "fanSpeed": fanSpeed,
            "timer": None  # 计时器
        }
        # 创建计时器
        timer = serviceTimer()
        serviceObj["timer"] = timer
        timer.start()
        cls.serviceQueue.append(serviceObj)

    @classmethod
    def removeRequest(cls, roomId):
        """从服务队列中移除请求"""
        serviceObj = cls.getServiceObject(roomId)
        if serviceObj and serviceObj["timer"]:
            # 移除计时器
            serviceObj["timer"].cancelTimer()
            # 遍历 serviceQueue 查找匹配的 serviceObj 并移除
            for obj in cls.serviceQueue:
                if obj["roomId"] == roomId:
                    cls.serviceQueue.remove(obj)
                    print(f"已经移除房间{roomId}的服务请求")
                    break  # 找到并移除后退出循环
        else:
            print(f"没有找到与 roomId {roomId} 对应的服务请求")

    @classmethod
    def contains(cls, roomId):
        """检查房���是否在服务队列中"""
        return any(sq["roomId"] == roomId for sq in cls.serviceQueue)

    @classmethod
    def getServiceObject(cls, roomId):
        """获取房间对应的服务对象"""
        for sq in cls.serviceQueue:
            if sq["roomId"] == roomId:
                return sq
        return None

    @classmethod
    def removeRequestNoCalculate(cls, roomId):
        """从服务队列中移除请求，不计算温度"""
        serviceObj = cls.getServiceObject(roomId)
        if serviceObj and serviceObj["timer"]:
            serviceObj["timer"].cancelTimer()
            # 遍历 serviceQueue 查找匹配的 serviceObj 并移除
            for obj in cls.serviceQueue:
                if obj["roomId"] == roomId:
                    cls.serviceQueue.remove(obj)
                    print(f"已经移除房间{roomId}的服务请求")
                    break  # 找到并移除后退出循环
        else:
            print(f"没有找到与 roomId {roomId} 对应的服务请求")
    @classmethod
    def updateFanSpeed(cls, roomId, fanSpeed):
        """更新服务队列中的风速"""
        i=0
        for sq in cls.serviceQueue:
            if sq["roomId"] == roomId:
                sq["fanSpeed"] = fanSpeed
                print(f"更新风速 - 房��: {roomId}, 新风速: {fanSpeed}")
                i=1
                break
        if i==0:
            print(f"房间 {roomId} 不在服务队列中")
    @classmethod
    def GetListLength(cls):
        return len(cls.serviceQueue)
    @classmethod
    def GetLeastTimeRoomId(cls):
        Compare = []
        
        # 遍历 serviceQueue 列表，获取每个房间的剩余时间和房间号
        for sq in cls.serviceQueue:
            Time = sq["timer"].GetRemainingTime()  # 获取每个房间的剩余时间
            RoomId = sq["roomId"]
            Compare.append([Time, RoomId])  # 将 Time 和 RoomId 放入 Compare 列表中
        if Compare:
            # 找到剩余时间最小的房间
            min_time_item = min(Compare, key=lambda x: x[0])  # 根据 Time 最小的项来比较
            return min_time_item[1]  # 返回最小时间对应的 RoomId
        else:
            return None

class WaitQueue:
    # 将队列变为类变量
    waitQueue = []
    @classmethod
    def getListLength(cls):
        return len(cls.waitQueue)
    @classmethod
    def addWait(cls, roomId, fanSpeed, priority):
        """添加等待请求到等待队列"""
        serviceObj = {
            "roomId": roomId,
            "fanSpeed": fanSpeed,
            "timer": None,  # 计时器
            "priority": priority
        }
        # 创建计时器
        waitserviceObj = {
            "roomId": roomId,
            "fanSpeed": fanSpeed,
            "priority": priority
        }
        if priority == 0:
            timer = waitingTimer(waitserviceObj, 60)
        else:
            timer = waitingTimer(waitserviceObj, 1/3)
        serviceObj["timer"] = timer
        timer.start()
        cls.waitQueue.append(serviceObj)
    @classmethod
    def getWaitObject(cls, roomId):
        """获取房间对应的等待对象"""
        for wq in cls.waitQueue:
            if wq["roomId"] == roomId:
                return wq
        return None
    @classmethod
    def removeRequest(cls, roomId):
        """从等待队列中移除请求"""
        print(f"移除房间{roomId}的等待请求")
        if cls.getWaitObject(roomId):
            # 先移除计时器
            cls.getWaitObject(roomId)["timer"].cancelTimer()
            # 再移除等待队列
            for obj in cls.waitQueue:
                if obj["roomId"] == roomId:
                    cls.waitQueue.remove(obj)
                    break  # 找到并移除后退出循环
        else:
            print(f"房间{roomId}不在等待队列中")

    @classmethod
    def contains(cls, roomId):
        """检查房间是否在等待队列中"""
        return any(wq["roomId"] == roomId for wq in cls.waitQueue)

    @classmethod
    def updateFanSpeed(cls, roomId, fanSpeed):
        """更新等待队列中的风速"""
        for wq in cls.waitQueue:
            if wq["roomId"] == roomId:
                wq["fanSpeed"] = fanSpeed
                print(f"更新风速 - 房间: {roomId}, 新风速: {fanSpeed}")
                break

    @classmethod
    def clearRequest(cls, roomId):
        """清除等待请求并终止定时器"""
        waitObj = cls.getWaitObject(roomId)
        if waitObj and waitObj["timer"]:
            waitObj["timer"].cancelTimer()
        cls.removeRequest(roomId)
    @classmethod
    def GetLeastTimeRoomId(cls):
        Compare = []
        for wq in cls.waitQueue:
            Time = wq["timer"].GetRemainingTime()
            RoomId = wq["roomId"]
            Compare.append([Time, RoomId])
        if Compare:
            min_time_item = min(Compare, key=lambda x: x[0])
            return min_time_item[1] 
        else:
            return None
    @classmethod
    def getWaitObject(cls, roomId):
        for wq in cls.waitQueue:
            if wq["roomId"] == roomId:
                return wq
        return None
    

# 调度器类，负责调度服务请求
class Scheduler:
    def __init__(self):
        self.maxServiceObjects = 3  # 服务对象上限
    def schedule(self, roomId, fanSpeed, Mode):
        # 检查房间是否已经在服务队列中
        print("----schedule开始----")
        serviceQueue = ServiceQueue()
        waitQueue = WaitQueue()
        if Mode == "开机":
            # 先看等待队列里和服务队列里有没有相同的房间号
            # 如果有，就不处理开机请求
            if waitQueue.contains(roomId) or serviceQueue.contains(roomId):
                print(f"房间号：{roomId}，在等待队列或服务队列中，不处理开机请求")
                return
            # 检查服务队列长度
            room = Room.getRoom(roomId)
            airConditioner = AirConditioner.powerOn(room,"制热")
            if serviceQueue.GetListLength() < self.maxServiceObjects:
                # 服务对数小于上限，直接分配服务对象
                serviceQueue.addServiceQueue(roomId, fanSpeed)
            else:
                # 服务对象数达到上限，添加到等待队列
                print(f"服务对象数已达上限，启动调度算法")
                self.schedule_poweron_algorithm(fanSpeed,roomId,serviceQueue,waitQueue)
        if Mode == "调风":
            # 检查风速是否和原来一样
            service_obj = serviceQueue.getServiceObject(roomId)
            if service_obj and service_obj["fanSpeed"] == fanSpeed:
                print(f"风速未改变，不处理调风请求")
                return
            wait_obj = waitQueue.getWaitObject(roomId)
            if wait_obj and wait_obj["fanSpeed"] == fanSpeed:
                print(f"风速未改变，不处理调风请求")
                return
            # 如果在服务队列中，则直接更新风速
            if serviceQueue.getServiceObject(roomId):
                AirConditioner.setFanSpeed(roomId,fanSpeed)
                serviceQueue.updateFanSpeed(roomId,fanSpeed)
            else:
                if waitQueue.contains(roomId):
                    print(f"在等待队列里，启动调度算法")
                    AirConditioner.setFanSpeed(roomId,fanSpeed)
                    waitQueue.updateFanSpeed(roomId,fanSpeed)
                    self.schedule_fanspeed_algorithm(fanSpeed,roomId,serviceQueue,waitQueue)
                else:
                    # 如果不在等待队列也不在服务队列里，则先看服务队列是否满
                    if serviceQueue.GetListLength() < self.maxServiceObjects:
                        serviceQueue.addServiceQueue(roomId,fanSpeed)
                    else:
                        AirConditioner.setFanSpeed(roomId,fanSpeed)
                        self.schedule_fanspeed_algorithm(fanSpeed,roomId,serviceQueue,waitQueue)

        print("----schedule结束----")
    def schedule_poweron_algorithm(self, FanSpeed, roomId, serviceQueue, waitQueue):
        """调度算法实现"""
        # 找出服务队列中风速小于目标风速的房间
        lowerSpeedRooms = []
        for service in serviceQueue.serviceQueue:
            if service["fanSpeed"] < FanSpeed:
                lowerSpeedRooms.append({
                    "roomId": service["roomId"],
                    "fanSpeed": service["fanSpeed"],
                    "remainingTime": service["timer"].GetRemainingTime() if service["timer"] else (0, 0)
                })
        
        if lowerSpeedRooms:
            #看服务队列里有没有风速小于该请求风速的，如果有，那就找出这些房间里风速最小的房间和其对应的房间号
            #如果只有一个，那么找到的这个房间被放置于等待队列
            #如果有多个，那么计时器倒计时最短的房间被放置于等待队列

            #找出风速最小的房间
            minFanSpeed = min(room["fanSpeed"] for room in lowerSpeedRooms)
            minSpeedRooms = [room for room in lowerSpeedRooms if room["fanSpeed"] == minFanSpeed]
            if len(minSpeedRooms) == 1:
                # 只有一个最小风速的房间
                roomToWait = minSpeedRooms[0]["roomId"]
            else:
                # 有多个最小风速的房间，选择剩余时间最短的
                minRemainingTime = float('inf')
                roomToWait = None
                for room in minSpeedRooms:
                    remainingMinutes, remainingSeconds = room["remainingTime"]
                    totalSeconds = remainingMinutes * 60 + remainingSeconds
                    if totalSeconds < minRemainingTime:
                        minRemainingTime = totalSeconds
                        roomToWait = room["roomId"]
        
            # 将选中的房间移到等待队列，新请求进入服务队列
            print(f"房间 {roomToWait} 被移至等待队列")
            serviceQueue.removeRequest(roomToWait)
            priority = 1
            waitQueue.addWait(roomToWait, minFanSpeed, priority)
            
            # 新请求进入服务队列
            print(f"房间 {roomId} 进入服务队列")
            serviceQueue.addServiceQueue(roomId, FanSpeed)
        else:
            # 先看服务对象的风速是否全部都和请求风速相同
            if all(service["fanSpeed"] == FanSpeed for service in serviceQueue.serviceQueue):
                # 如果相同，则新请求进入等待队列
                priority = 1
                waitQueue.addWait(roomId, FanSpeed, priority)
            else:
                # 如果不同，则新请求以最低优先级进入等待队列
                priority = 0
                waitQueue.addWait(roomId, FanSpeed, priority)
    def schedule_fanspeed_algorithm(self, FanSpeed, roomId, serviceQueue, waitQueue):
        """调度算法实现"""
        # 找出服务队列中风速小于目标风速的房间
        lowerSpeedRooms = []
        for service in serviceQueue.serviceQueue:
            if service["fanSpeed"] < FanSpeed:
                lowerSpeedRooms.append({
                    "roomId": service["roomId"],
                    "fanSpeed": service["fanSpeed"],
                    "remainingTime": service["timer"].GetRemainingTime() if service["timer"] else (0, 0)
                })
        
        if lowerSpeedRooms:
            #看服务队列里有没有风速小于该请求风速的，如果有，那就找出这些房间里风速最小的房间和其对应的房间号
            #如果只有一个，那么找到的这个房间被放置于等待队列
            #如果有多个，那么计时器倒计时最短的房间被放置于等待队列

            #找出风速最小的房间
            minFanSpeed = min(room["fanSpeed"] for room in lowerSpeedRooms)
            minSpeedRooms = [room for room in lowerSpeedRooms if room["fanSpeed"] == minFanSpeed]
            if len(minSpeedRooms) == 1:
                # 只有一个最小风速的房间
                roomToWait = minSpeedRooms[0]["roomId"]
            else:
                # 有多个最小风速的房间，选择剩余时间最短的
                minRemainingTime = float('inf')
                roomToWait = None
                for room in minSpeedRooms:
                    remainingMinutes, remainingSeconds = room["remainingTime"]
                    totalSeconds = remainingMinutes * 60 + remainingSeconds
                    if totalSeconds < minRemainingTime:
                        minRemainingTime = totalSeconds
                        roomToWait = room["roomId"]
        
            # 将选中的房间移到等待队列，新请求进入服务队列
            print(f"房间 {roomToWait} 被移至等待队列")
            serviceQueue.removeRequest(roomToWait)
            priority = 1
            waitQueue.addWait(roomToWait, minFanSpeed, priority)
            
            # 新请求进入服务队列
            print(f"房间 {roomId} 进入服务队列")
            serviceQueue.addServiceQueue(roomId, FanSpeed)
            waitQueue.removeRequest(roomId)
        else:
            print("无事发生")
    def changeTemp(self, roomId, targetTemp):
        """改变温度"""
        # 检查房间是否有空调实例
        if AirConditioner.findAirConditioner(roomId):
            # 调用 schedule 函数
            AirConditioner.setTargetTemp(roomId,targetTemp)
            return True
        else:
            print(f"房间 {roomId} 没有空调实例")
            return False

class waitingTimer:
    def __init__(self, serviceObj, durationMinutes=2):
        self.serviceObj = serviceObj
        self.durationMinutes = durationMinutes
        self.timer = None
        self.start_time = None
    def start(self):
        """启动计时器"""
        self.start_time = datetime.now()
        self.timer = threading.Timer(20, self.onTimeUp)  # 转换秒
        self.timer.start()
    def onTimeUp(self):  
        """时间到达后触发的回调函数"""
        print(f"房间号：{self.serviceObj['roomId']}，等待队列计时器到期")
        # 从服务队列中移除计时剩余时长最短请求,并将其添加到等待队列
        serviceQueue = ServiceQueue()
        waitQueue = WaitQueue()
        if serviceQueue.GetListLength() < 3:
            # 获得计时器的房间的风速和房间号
            fanSpeed = self.serviceObj["fanSpeed"]
            roomId = self.serviceObj["roomId"]
            # 把计时器的房间移动到服务队列
            serviceQueue.addServiceQueue(roomId, fanSpeed)
            waitQueue.clearRequest(roomId)
        else:
            roomIdToRemove = serviceQueue.GetLeastTimeRoomId()
            RequestToRemove = serviceQueue.getServiceObject(roomIdToRemove)
            fanSpeed = RequestToRemove["fanSpeed"]
            serviceQueue.removeRequest(roomIdToRemove)
            priority = 1
            waitQueue.addWait(roomIdToRemove, fanSpeed, priority)
            print(f"房间号：{roomIdToRemove}，加入等待队列")
            # 获得计时器的房间的风速和房间号
            fanSpeed = self.serviceObj["fanSpeed"]
            roomId = self.serviceObj["roomId"]
            # 把计时器的房间移动到服务队列
            serviceQueue.addServiceQueue(roomId, fanSpeed)
            waitQueue.clearRequest(roomId)
        print(f"房间号：{roomId}，加入服务队列")
        print("等待队列计时器处理完毕")
    def cancelTimer(self):
        """终止定时器并打印信息"""
        if self.timer:
            self.timer.cancel()
    def GetRemainingTime(self):
        """获取剩余时间"""
        if not self.start_time:
            return "计时器尚未启动"  

        # 计算已经过去的时间
        elapsed_time = datetime.now() - self.start_time
        
        remaining_time = timedelta(minutes=25) - elapsed_time

        if remaining_time <= timedelta(seconds=0):
            return "0分 0秒"  # 如果剩余时间小于等于 0，表示计时结束

        # 将剩余时间转换为分钟和秒
        remaining_minutes = remaining_time.seconds // 60
        remaining_seconds = remaining_time.seconds % 60

        return remaining_minutes,remaining_seconds
class serviceTimer:
    def __init__(self):  
        self.timer = None
        self.start_time = None
    def start(self):
        """启动计时器"""
        self.start_time = datetime.now()
        self.timer = threading.Timer(25 * 60, self.onTimeUp)  # 转换秒
        self.timer.start()
    def GetRemainingTime(self):
        """获取剩余时间"""
        if not self.start_time:
            return "计时器尚未启动"  # 1

        # 计算已经过去的时间
        elapsed_time = datetime.now() - self.start_time
        
        remaining_time = timedelta(minutes=25) - elapsed_time

        if remaining_time <= timedelta(seconds=0):
            return "0分 0秒"  # 如果剩余时间小于等于 0，表示计时结束

        # 将剩余时间转换为分钟和秒
        remaining_minutes = remaining_time.seconds // 60
        remaining_seconds = remaining_time.seconds % 60

        return remaining_minutes,remaining_seconds

    def onTimeUp(self):
        """计时器到期时调用的回调函数"""
        print(f"计时结束")

    def cancelTimer(self):
        if self.timer:
            self.timer.cancel()
class returnTempTimer:
    def __init__(self):  
        self.timer = None
        self.start_time = None
    def start(self):
        """启动计时器"""
        self.start_time = datetime.now()
        self.timer = threading.Timer(25 * 60, self.onTimeUp)  # 转换秒
        self.timer.start()
    def GetRemainingTime(self):
        """获取剩余时间"""
        if not self.start_time:
            return "计时器尚未启动"  # 1

        # 计算已经过去的时间
        elapsed_time = datetime.now() - self.start_time
        
        remaining_time = timedelta(minutes=25) - elapsed_time

        if remaining_time <= timedelta(seconds=0):
            return "0分 0秒"  # ��果剩余时间小于等于 0，表示计时结束

        # 将剩余时间转换为分钟和秒
        remaining_minutes = remaining_time.seconds // 60
        remaining_seconds = remaining_time.seconds % 60

        return remaining_minutes,remaining_seconds

    def onTimeUp(self):
        """计时器到期时调用的回调函数"""
        print(f"计时结束")

    def cancelTimer(self):
        if self.timer:
            self.timer.cancel()

# class RoomTimer:
#     def __init__(self, newroomId):
#         self.running = False
#         self.count = 0  # 用于追踪计数
#         self.roomId = newroomId

#     def startTimer(self):
#         """启动定时器"""
#         if not self.running:
#             self.running = True
#             self.thread = threading.Thread(target=self.run)
#             self.thread.daemon = True
#             self.thread.start()
#             print(f"{self.roomId}空调关机，开始回温")  # 这里打印回温开始信息

#     def run(self):
#         """定时器运行函数"""
#         while self.running:
#             time.sleep(self.interval)  # 等待一段时间
#             if not AirConditioner.findAirConditioner(self.roomId):
#                 # 如果空调关闭，执行回温
#                 if abs(self.currentTemp - self.initialTemp) > 0.1:
#                     # 当前温度逐渐接近初始温度
#                     if self.currentTemp < self.initialTemp:
#                         self.currentTemp += 0.5
#                     else:
#                         self.currentTemp -= 0.5
#                     print(f"{self.roomId}回温后，当前温度：{self.currentTemp}°C")  # 这里打印回温后的温度

#     def cancel(self):
#         """取消计时器"""
#         self.running = False
#         print("计时器停止...")

#     def _first_cycle_A(self):
#         """第一次循环调用A"""
#         if not self.running:
#             return
#         self._call_function_A()
#         # 1秒后调用B
#         threading.Timer(1, self._first_cycle_B).start()

#     def _first_cycle_B(self):
#         """第一次循环调用B"""
#         if not self.running:
#             return
#         self._call_function_B()
#         self.count += 1
#         # 准备后续循环
#         self._next_cycle()

#     def _next_cycle(self):
#         """后续循环：每次9秒后调用A，然后1秒后调用B，重复"""
#         if not self.running:
#             return
#         threading.Timer(9, self._next_cycle_A).start()

#     def _next_cycle_A(self):
#         if not self.running:
#             return
#         self._call_function_A()
#         threading.Timer(1, self._next_cycle_B).start()

#     def _next_cycle_B(self):
#         if not self.running:
#             return
#         self._call_function_B()
#         self.count += 1
#         # 再次进入下一轮循环
#         self._next_cycle()

#     def _call_function_A(self):
#         Room.updateTemp(self.roomId)

#     def _call_function_B(self):
#         Room.updateState(self.roomId)
class RoomTimer:
    def __init__(self, newroomId):
        self.running = False
        self.count = 0  # 用于追踪计数
        self.roomId = newroomId

    def startTimer(self):
        """开始计时器：第一次等待7秒后调用A，再等待1秒调用B"""
        if not self.running:
            self.running = True
            # 第一次：7秒后调用A
            threading.Timer(7, self._first_cycle_A).start()
    
    def cancel(self):
        """取消计时器"""
        self.running = False
        print("计时器停止...")

    def _first_cycle_A(self):
        """第一次循环调用A"""
        if not self.running:
            return
        self._call_function_A()
        # 1秒后调用B
        threading.Timer(1, self._first_cycle_B).start()

    def _first_cycle_B(self):
        """第一次循环调用B"""
        if not self.running:
            return
        self._call_function_B()
        self.count += 1
        # 准备后续循环
        self._next_cycle()

    def _next_cycle(self):
        """后续循环：每次9秒后调用A，然后1秒后调用B，重复"""
        if not self.running:
            return
        threading.Timer(9, self._next_cycle_A).start()

    def _next_cycle_A(self):
        if not self.running:
            return
        self._call_function_A()
        threading.Timer(1, self._next_cycle_B).start()

    def _next_cycle_B(self):
        if not self.running:
            return
        self._call_function_B()
        self.count += 1
        # 再次进入下一轮循环
        self._next_cycle()

    def _call_function_A(self):
        Room.updateTemp(self.roomId)

    def _call_function_B(self):
        Room.updateState(self.roomId)

# 顾客类
class Customer:
    # 存储所有顾客实例的列表
    customerList = []
    
    def __init__(self, custId, custName, phoneNumber, checkInDate):
        self.custId = custId
        self.custName = custName
        self.phoneNumber = phoneNumber
        self.checkInDate = checkInDate
        self.roomId = None  # 关联的房间号
    
    @classmethod
    def createCustomer(cls, custId, custName, phoneNumber, checkInDate):
        """创建新顾客"""
        # 检查是否已存在相同ID的顾客
        if any(cust.custId == custId for cust in cls.customerList):
            print(f"顾客ID {custId} 已存在")
            return False
            
        # 创建新顾实例
        newCustomer = Customer(custId, custName, phoneNumber, checkInDate)
        cls.customerList.append(newCustomer)
        print(f"创建新顾客 - ID: {custId}, 姓名: {custName}")
        return True
    
    @classmethod
    def findCustomer(cls, custId):
        """查找顾客"""
        for customer in cls.customerList:
            if customer.custId == custId:
                return customer
        return None

# 住宿订单类
class AccommodationOrder:
    # 存储所有订单实例的列表
    orderList = []
    
    def __init__(self, customerId, roomId, checkInDate):
        self.customerId = customerId
        self.roomId = roomId
        self.checkInDate = checkInDate
        self.status = "active"  # active 或 completed
    
    @classmethod
    def createOrder(cls, customerId, roomId):
        """创建新订单"""
        try:
            # 检查房间是否存在
            room = Room.getRoom(roomId)
            if not room:
                print(f"房间 {roomId} 不存在")
                return False
                
            # 检查房间是否已被占用
            if room.isOccupied:
                print(f"房间 {roomId} 已被占用")
                return False
            
            # 查找顾客
            customer = Customer.findCustomer(customerId)
            if not customer:
                print(f"未找到顾客 ID: {customerId}")
                return False
            
            # 创建新订单
            newOrder = AccommodationOrder(customerId, roomId, customer.checkInDate)
            cls.orderList.append(newOrder)
            
            # 更新顾客关联的房间号
            customer.roomId = roomId
            
            # 更新房间状态
            room.isOccupied = True
            room.currentCustomerId = customerId
            room.checkInTime = customer.checkInDate
            print(f"房间 {roomId} 状态已更新 - 入住顾客ID: {customerId}")
            
            return True
            
        except Exception as e:
            print(f"创建订单时发生错误: {str(e)}")
            return False
    
    @classmethod
    def findActiveOrderByRoom(cls, roomId):
        """查找房间的活动订单"""
        for order in cls.orderList:
            if order.roomId == roomId and order.status == "active":
                return order
        return None

    @classmethod
    def checkout(cls, roomId):
        """处理退房"""
        try:
            # 1. 查找活动订单
            order = cls.findActiveOrderByRoom(roomId)
            if not order:
                print(f"房间 {roomId} 没有活动订单")
                return None
                
            # 2. 查找顾客信息
            customer = Customer.findCustomer(order.customerId)
            if not customer:
                print(f"未找到顾客信息")
                return None
                
            # 获取房间对象
            room = Room.getRoom(roomId)
            if not room:
                print(f"未找到房间信息")
                return None
            
            # 3. 计算费用
            from datetime import datetime
            check_out_time = datetime.now()
            check_in_time = datetime.strptime(order.checkInDate, "%Y-%m-%dT%H:%M")
            days = (check_out_time - check_in_time).days + 1
            
            # 4. 计算各项费用
            # 根据房间号设置基础费用
            base_fee_per_day = {
                101: 100,
                102: 125,
                103: 150,
                104: 200,
                105: 100
            }.get(room.roomId, 100)  # 默认100
            
            accommodation_fee = days * base_fee_per_day
            
            # 计算空调费用
            # 每度温度变化收费1元，与风速无关
            ac_fee = room.total_temp_change   # 每度温度变化1元
            
            # 重置温度变化计数
            room.total_temp_change = 0
            
            total_fee = accommodation_fee + ac_fee
            
            # 5. 更新状态
            order.status = "completed"
            room.isOccupied = False
            room.currentCustomerId = None
            
            # 返回结账详情
            checkout_details = {
                "customer_name": customer.custName,
                "check_in_time": check_in_time.strftime("%Y-%m-%d %H:%M"),
                "check_out_time": check_out_time.strftime("%Y-%m-%d %H:%M"),
                "days": days,
                "base_fee_per_day": base_fee_per_day,
                "accommodation_fee": accommodation_fee,
                "ac_fee": round(ac_fee, 2),  # 保留两位小数
                "total_fee": round(total_fee, 2)
            }
            
            return checkout_details
            
        except Exception as e:
            print(f"结账过程中发生错误: {str(e)}")
            return None

# 前台类
class Receptionist:
    @staticmethod
    def registerCustomer(custId, custName, phoneNumber, checkInDate):
        """注册顾客信息"""
        return Customer.createCustomer(custId, custName, phoneNumber, checkInDate)
    
    @staticmethod
    def checkRoomState(date):
        """检查房间状态"""
        roomStates = []
        for room in Room.RoomList:
            # 查找房间是否有活动订单
            order = AccommodationOrder.findActiveOrderByRoom(room.roomId)
            state = {
                "room_id": room.roomId,
                "status": "已入住" if order else "空闲",
                "customer": None
            }
            
            if order:
                customer = Customer.findCustomer(order.customerId)
                if customer:
                    state["customer"] = customer.custName
                    
            roomStates.append(state)
            
        return roomStates
    
    @staticmethod
    def createAccommodationOrder(customerId, roomId):
        """创建住宿订单"""
        return AccommodationOrder.createOrder(customerId, roomId)