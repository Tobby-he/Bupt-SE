// 服务器配置
const SERVER_URL = 'http://127.0.0.1:8000/api/';

// API 函数
async function apiRequest(endpoint, method, data) {
    try {
        const response = await fetch(SERVER_URL + endpoint, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            throw new TypeError("返回的不是 JSON 格式!");
        }

        return await response.json();
    } catch (error) {
        console.error('API请求失败:', error);
        throw error;
    }
}

// 页面切换函数
function switchPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    document.querySelectorAll('.nav-button').forEach(button => {
        button.classList.remove('active');
    });
    
    document.getElementById(pageId).classList.add('active');
    document.querySelector(`[onclick="switchPage('${pageId}')"]`).classList.add('active');
    
    // 如果是结账页面，重置表单和弹窗
    if (pageId === 'check-out') {
        document.getElementById('checkout-room-id').value = '';
        document.getElementById('checkout-details').style.display = 'none';
        window.currentCheckout = null;
    }
}

// 顾客注册函数
async function registerCustomer() {
    const custId = document.getElementById('cust-id').value;
    const custName = document.getElementById('cust-name').value;
    const phoneNumber = document.getElementById('phone-number').value;
    const checkInDate = document.getElementById('check-in-date').value;

    // 添加输入验证
    if (!custId || !custName || !phoneNumber || !checkInDate) {
        alert('请填写所有必填字段');
        return;
    }

    try {
        const response = await apiRequest('register-customer/', 'POST', {
            cust_id: custId,
            cust_name: custName,
            number: phoneNumber,
            date: checkInDate
        });

        if (response.status === 'success') {
            alert('顾客注册成功！');
            clearRegistrationForm();
        } else {
            alert('注册失败：' + response.message);
        }
    } catch (error) {
        console.error('注册失败:', error);
        alert('注册失败，请检查网络连接或联系管理员');
    }
}

// 查询房间状态函数
async function checkRoomState() {
    const queryDate = document.getElementById('query-date').value;

    try {
        const response = await apiRequest('check-room-state/', 'POST', {
            date: queryDate
        });

        if (response.status === 'success') {
            displayRoomStates(response.room_states);
        } else {
            alert('查询失败：' + response.message);
        }
    } catch (error) {
        alert('查询失败，请稍后重试');
    }
}

// 创建住宿订单函数
async function createAccommodationOrder() {
    const customerId = document.getElementById('customer-id').value;
    let roomId = document.getElementById('room-id').value;

    // 验证房间号是否在有效范围内
    roomId = parseInt(roomId);
    if (isNaN(roomId) || roomId < 101 || roomId > 105) {
        alert('请输入有效的房间号（101-105）');
        return;
    }

    if (!customerId) {
        alert('请输入顾客ID');
        return;
    }

    try {
        const response = await apiRequest('create-accommodation-order/', 'POST', {
            customer_id: customerId,
            room_id: roomId
        });

        if (response.status === 'success') {
            alert('订单创建成功！');
            clearOrderForm();
            // 刷新房间状态
            checkRoomState();
        } else {
            alert('创建失败：' + response.message);
        }
    } catch (error) {
        console.error('创建订单失败:', error);
        alert('创建订单失败，请检查网络连接或联系管理员');
    }
}

// 显示房间状态函数
function displayRoomStates(roomStates) {
    const grid = document.getElementById('room-status-grid');
    grid.innerHTML = '';

    // 如果没有房间状态数据，创建默认的房间卡片
    if (roomStates.length === 0) {
        // 修改为101-105的房间号
        const defaultRooms = [101, 102, 103, 104, 105];
        defaultRooms.forEach(roomId => {
            const card = document.createElement('div');
            card.className = 'room-card';
            card.innerHTML = `
                <h3>房间 ${roomId}</h3>
                <p>状态: <span class="status available">空闲</span></p>
            `;
            grid.appendChild(card);
        });
        return;
    }

    // 按房间号排序
    roomStates.sort((a, b) => a.room_id - b.room_id);

    // 创建房间状态卡片
    roomStates.forEach(room => {
        const card = document.createElement('div');
        card.className = 'room-card';
        card.innerHTML = `
            <h3>房间 ${room.room_id}</h3>
            <p>状态: <span class="status ${getStatusClass(room.status)}">${room.status}</span></p>
            ${room.customer ? `<p>入住顾客: ${room.customer}</p>` : ''}
            ${room.check_in_time ? `<p>入住时间: ${formatDateTime(room.check_in_time)}</p>` : ''}
        `;
        grid.appendChild(card);
    });
}

// 修改房间状态样式类函数
function getStatusClass(status) {
    switch (status) {
        case '空闲': return 'available';
        case '已入住': return 'occupied';
        case '已预订': return 'reserved';
        case '维护中': return 'maintenance';
        default: return 'available'; // 默认显示为空闲
    }
}

// 清空表单函数
function clearRegistrationForm() {
    document.getElementById('cust-id').value = '';
    document.getElementById('cust-name').value = '';
    document.getElementById('phone-number').value = '';
    document.getElementById('check-in-date').value = '';
}

function clearOrderForm() {
    document.getElementById('customer-id').value = '';
    document.getElementById('room-id').value = '';
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', () => {
    // 设置当前日期为默认查询日期
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('query-date').value = today;
    
    // 初始查询房间状态
    checkRoomState();
    
    // 为房间号输入框添加验证
    const roomIdInput = document.getElementById('room-id');
    if (roomIdInput) {
        roomIdInput.addEventListener('input', function() {
            const roomId = parseInt(this.value);
            if (!validateRoomId(roomId) && this.value !== '') {
                this.setCustomValidity('请输入有效的房间号（101-105）');
            } else {
                this.setCustomValidity('');
            }
        });
    }
});

// 处理结账
async function processCheckout() {
    const roomId = document.getElementById('checkout-room-id').value;
    
    if (!validateRoomId(roomId)) {
        alert('请输入有效的房间号（101-105）');
        return;
    }
    
    try {
        const response = await apiRequest('process-checkout/', 'POST', {
            room_id: parseInt(roomId)
        });
        
        if (response.status === 'success') {
            // 显示结账详情
            const details = response.data;
            const detailsHtml = `
                <div class="fee-item">
                    <span>顾客姓名：</span>
                    <span>${details.customer_name}</span>
                </div>
                <div class="fee-item">
                    <span>入住时间：</span>
                    <span>${formatDateTime(details.check_in_time)}</span>
                </div>
                <div class="fee-item">
                    <span>退房时间：</span>
                    <span>${formatDateTime(details.check_out_time)}</span>
                </div>
                <div class="fee-item">
                    <span>住宿天数：</span>
                    <span>${details.days}天</span>
                </div>
                <div class="fee-item">
                    <span>房间基础费用：</span>
                    <span>￥${details.base_fee_per_day}/天</span>
                </div>
                <div class="fee-item">
                    <span>住宿费用：</span>
                    <span>￥${details.accommodation_fee}</span>
                </div>
                <div class="fee-item">
                    <span>空调使用费用：</span>
                    <span>￥${details.ac_fee}</span>
                </div>
                <div class="total-fee">
                    <span>总计费用：</span>
                    <span>￥${details.total_fee}</span>
                </div>
            `;
            
            document.getElementById('checkout-info').innerHTML = detailsHtml;
            document.getElementById('checkout-details').style.display = 'block';
            
            window.currentCheckout = {
                roomId: roomId,
                totalFee: details.total_fee,
                checkOutTime: details.check_out_time
            };
        } else {
            alert('结账失败：' + response.message);
        }
    } catch (error) {
        console.error('结账失败:', error);
        alert('结账失败：' + (error.message || '请检查网络连接或联系管理员'));
    }
}

// 确认支付
async function confirmPayment() {
    if (!window.currentCheckout) {
        alert('没有待支付的账单');
        return;
    }
    
    try {
        // 向后端发送确认支付请求
        const response = await apiRequest('confirm-payment/', 'POST', {
            room_id: window.currentCheckout.roomId,
            total_fee: window.currentCheckout.totalFee,
            checkout_time: window.currentCheckout.checkOutTime
        });
        
        if (response.status === 'success') {
            // 更新前端显示
            document.getElementById('checkout-details').style.display = 'none';
            document.getElementById('checkout-room-id').value = '';
            window.currentCheckout = null;
            
            // 刷新房间状态
            await checkRoomState();
            
            alert('支付成功！');
        } else {
            throw new Error(response.message || '支付失败');
        }
    } catch (error) {
        console.error('支付失败:', error);
        alert('支付失败：' + error.message);
    }
}

// 取消结账
async function cancelCheckout() {
    try {
        if (window.currentCheckout) {
            // 可选：通知后端取消结账操作
            await apiRequest('cancel-checkout/', 'POST', {
                room_id: window.currentCheckout.roomId
            });
        }
        
        // 重置前端状态
        document.getElementById('checkout-details').style.display = 'none';
        document.getElementById('checkout-room-id').value = '';
        window.currentCheckout = null;
        
        // 刷新房间状态，确保显示正确
        await checkRoomState();
    } catch (error) {
        console.error('取消结账失败:', error);
        alert('取消结账失败，请重试');
    }
}

// 添加日期格式化函数
function formatDateTime(dateTimeStr) {
    const date = new Date(dateTimeStr);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 添加房间号验证函数
function validateRoomId(roomId) {
    const numRoomId = parseInt(roomId);
    return !isNaN(numRoomId) && numRoomId >= 101 && numRoomId <= 105;
}