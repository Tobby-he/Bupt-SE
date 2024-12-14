let currentTemp = 25;
let fanSpeed = 0; // 0 代表关闭，1,2,3 代表低中高风速
let isOn = false;

function increaseTemp() {
    if (isOn && currentTemp < 30) {
        currentTemp++;
        updateDisplayTemp();
    }
}

function decreaseTemp() {
    if (isOn && currentTemp > 18) {
        currentTemp--;
        updateDisplayTemp();
    }
}

function togglePower() {
    isOn = !isOn;
    const tempInput = document.getElementById('temp-input');
    const setTempButton = tempInput.nextElementSibling;
    
    if (isOn) {
        document.getElementById('ac-temp').value = currentTemp;
        tempInput.disabled = false;
        setTempButton.disabled = false;
        updateDisplayTemp();
    } else {
        document.getElementById('display-temp').textContent = '关';
        tempInput.disabled = true;
        setTempButton.disabled = true;
        tempInput.value = "";
    }
    sendToServer("togglePower", { isOn: isOn });
}

function changeFanSpeed() {
    if (isOn) {
        fanSpeed = fanSpeed + 1;
        if (fanSpeed > 3) {
            fanSpeed = 0;
        }
        updateFanSpeedIcon();
        if (fanSpeed > 0) {
            sendToServer("changeFanSpeed", { speed: fanSpeed });
        }
    }
}

function updateDisplayTemp() {
    if (isOn) {
        const tempElement = document.getElementById('display-temp');
        tempElement.textContent = `${currentTemp}°`;
        document.getElementById('ac-temp').value = currentTemp;
        document.getElementById('temp-input').value = currentTemp;
    }
}

function updateFanSpeedIcon() {
    const iconElement = document.getElementById('fan-speed-icon');
    
    // 始终创建三个档位条，不论是否为0档
    let bars = '';
    for (let i = 1; i <= 3; i++) {
        bars += `<span class="speed-bar${i <= fanSpeed ? ' active' : ''}"></span>`;
    }
    iconElement.innerHTML = bars;
}

// 初始化
updateDisplayTemp();
updateFanSpeedIcon();

// 滑动条变化时更新显示温度
document.getElementById('ac-temp').addEventListener('input', function() {
    if (isOn) {
        currentTemp = parseInt(this.value, 10);
        updateDisplayTemp();
    }
});

// 页面切换功能
function switchPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
        page.style.opacity = '0';
    });
    
    const targetPage = document.getElementById(pageId);
    targetPage.classList.add('active');
    
    // 添加简单的淡入效果
    setTimeout(() => {
        targetPage.style.opacity = '1';
    }, 100);
    
    // 只有在切换主要页面时才更新导航按钮状态
    if (pageId === 'room-management' || pageId === 'bill-management') {
        document.querySelectorAll('.nav-button').forEach(button => {
            button.classList.remove('active');
        });
        document.querySelector(`[onclick="switchPage('${pageId}')"]`).classList.add('active');
    }
}

// 初始化房间数据（示例）
function initializeRooms() {
    const rooms = [
        { number: '101', temp: 26, acStatus: '运行中', setTemp: 22, occupied: true, fanSpeed: 2 },
        { number: '102', temp: 24, acStatus: '关闭', setTemp: 25, occupied: false, fanSpeed: 0 },
        { number: '103', temp: 25, acStatus: '运行中', setTemp: 23, occupied: true, fanSpeed: 2 },
        { number: '104', temp: 23, acStatus: '关闭', setTemp: 24, occupied: false, fanSpeed: 0 },
    ];
    
    const roomGrid = document.querySelector('.room-grid');
    roomGrid.innerHTML = '';
    
    rooms.forEach(room => {
        const roomCard = createRoomCard(room);
        roomGrid.appendChild(roomCard);
    });
}

// 创建房间卡片
function createRoomCard(room) {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'room-card';
    cardDiv.innerHTML = `
        <div class="room-header">
            <h3>房间 ${room.number}</h3>
            <span class="status ${room.occupied ? 'occupied' : ''}">${room.occupied ? '已入住' : '空闲'}</span>
        </div>
        <div class="room-info">
            <p>当前温度: <span class="current-temp">${room.temp}°C</span></p>
            <p>空调状态: <span class="ac-status">${room.acStatus}</span></p>
            <p>设定温度: <span class="target-temp">${room.setTemp}°C</span></p>
            <p>风速: <span class="fan-speed">${getFanSpeedText(room.fanSpeed)}</span></p>
        </div>
        <div class="room-controls">
            <button class="control-btn" onclick="showDetails('${room.number}')">查看详情</button>
            <button class="control-btn" onclick="showControl('${room.number}')">控制空调</button>
        </div>
    `;
    return cardDiv;
}

// 添加风速转换函数
function getFanSpeedText(speed) {
    switch (speed) {
        case 1:
            return '低速';
        case 2:
            return '中速';
        case 3:
            return '高速';
        default:
            return '关闭';
    }
}

// 添加显示详情和控制面板的函数
function showDetails(roomNumber) {
    document.getElementById('detail-room-number').textContent = roomNumber;
    // 这里可以添加从后端获取详细数据的逻辑
    switchPage('ac-details');
}

function showControl(roomNumber) {
    document.getElementById('control-room-number').textContent = roomNumber;
    // 这里可以添加从后端获取空调状态的逻辑
    switchPage('ac-control');
}

// 添加setTemperature函数
function setTemperature() {
    if (!isOn) return;
    
    const tempInput = document.getElementById('temp-input');
    const newTemp = parseInt(tempInput.value);
    
    if (newTemp < 18 || newTemp > 30) {
        alert('温度必须在18-30度之间');
        tempInput.value = currentTemp;
        return;
    }
    
    sendToServer("tempSlider", { temperature: newTemp });
    currentTemp = newTemp;
    updateDisplayTemp();
}

// 添加更新房间状态的函数
function updateRoomStatus(roomNumber, data) {
    console.log('Updating room status:', roomNumber, data); // 添加调试日志
    
    const roomCards = document.querySelectorAll('.room-card');
    roomCards.forEach(card => {
        const roomTitle = card.querySelector('h3').textContent.trim();
        console.log('Checking room:', roomTitle); // 添加房间检查日志
        
        if (roomTitle === `房间 ${roomNumber}`) {
            console.log('Found room card:', roomTitle); // 添加匹配日志
            
            // 更新当前温度
            const currentTempElement = card.querySelector('.current-temp');
            if (currentTempElement) {
                currentTempElement.textContent = `${data.currentTemp}°C`;
                console.log('Updated current temp:', data.currentTemp); // 添加温度更新日志
            }
            
            // 更新目标温度
            const targetTempElement = card.querySelector('.target-temp');
            if (targetTempElement && data.targetTemp !== undefined) {
                targetTempElement.textContent = `${data.targetTemp}°C`;
                console.log('Updated target temp:', data.targetTemp); // 添加目标温度更新日志
            }
            
            // 更新风速
            const fanSpeedElement = card.querySelector('.fan-speed');
            if (fanSpeedElement && data.fanSpeed !== undefined) {
                fanSpeedElement.textContent = getFanSpeedText(data.fanSpeed);
                console.log('Updated fan speed:', data.fanSpeed); // 添加风速更新日志
            }
            
            // 更新空调状态
            const acStatusElement = card.querySelector('.ac-status');
            if (acStatusElement) {
                acStatusElement.textContent = data.isOn ? '运行中' : '关闭';
                console.log('Updated AC status:', data.isOn); // 添加状态更新日志
            }
        }
    });
}

// 修改轮询函数
function startPolling() {
    setInterval(async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/api/room_status/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ 
                    room_id: 3  // 房间103
                }),
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('Received data:', data); // 添加数据日志
                
                if (data.status === 'success') {
                    // 更新房间状态
                    updateRoomStatus('103', {
                        currentTemp: data.data.currentTemp,
                        targetTemp: data.data.targetTemp,
                        fanSpeed: data.data.fanSpeed,
                        isOn: data.data.isOn1
                    });
                }
            } else {
                console.error('获取房间状态失败:', response.statusText);
            }
        } catch (error) {
            console.error('获取房间状态失败:', error);
        }
    }, 2000); // 改为每2秒更新一次，方便测试
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing...'); // 添加调试日志
    
    const tempInput = document.getElementById('temp-input');
    const setTempButton = tempInput.nextElementSibling;
    
    // 初始状态为关机，禁用输入框和按钮
    tempInput.disabled = true;
    setTempButton.disabled = true;
    tempInput.value = ""; // 清空输入框
    document.getElementById("display-temp").textContent = "关";
    
    // 确保风速图标显示
    const iconElement = document.getElementById("fan-speed-icon");
    if (iconElement) {  // 添加检查确保元素存在
        let bars = '';
        for (let i = 1; i <= 3; i++) {
            bars += `<span class="speed-bar${i <= fanSpeed ? ' active' : ''}"></span>`;
        }
        iconElement.innerHTML = bars;
    }
    
    initializeRooms();
    console.log('Rooms initialized, starting polling...'); // 添加调试日志
    startPolling();
});