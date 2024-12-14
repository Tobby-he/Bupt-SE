// script.js

// 获取所有登录按钮和表单
const userLoginBtn = document.getElementById('userLoginBtn');
const adminLoginBtn = document.getElementById('adminLoginBtn');
const frontDeskLoginBtn = document.getElementById('frontDeskLoginBtn');

const userLoginForm = document.getElementById('userLoginForm');
const adminLoginForm = document.getElementById('adminLoginForm');
const frontDeskLoginForm = document.getElementById('frontDeskLoginForm');

// 服务器配置
const SERVER_URL = 'http://127.0.0.1:8000/api/';

// 处理顾客登录
async function customerLogin() {
    const roomNumber = document.getElementById('room-number').value;
    const customerId = document.getElementById('customer-id').value;
    
    if (!roomNumber || !customerId) {
        document.getElementById('error-message').innerText = '请填写所有字段';
        return;
    }
    
    try {
        const response = await fetch(SERVER_URL + 'verify-customer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_id: roomNumber,
                customer_id: customerId
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // 保存登录信息到 localStorage
            localStorage.setItem('currentCustomer', JSON.stringify({
                roomId: roomNumber,
                customerId: customerId
            }));
            
            // 登录成功，跳转到空调控制页面
            window.location.href = '../html/index.html';
        } else {
            document.getElementById('error-message').innerText = data.message || '验证失败';
        }
    } catch (error) {
        console.error('登录失败:', error);
        document.getElementById('error-message').innerText = '登录失败，请检查网络连接';
    }
}

// 处理管理员登录
function adminLogin() {
    const adminUsername = document.getElementById('adminUsername').value;
    const adminPassword = document.getElementById('adminPassword').value;
    
    if (adminUsername === 'admin' && adminPassword === '123') {
        // 保存管理员登录状态
        localStorage.setItem('adminLoggedIn', 'true');
        window.location.href = '../html/admin_index.html';
    } else {
        document.getElementById('error-message').innerText = '管理员账号或密码错误';
    }
}

// 处理前台登录
function frontDeskLogin() {
    const username = document.getElementById('frontDeskUsername').value;
    const password = document.getElementById('frontDeskPassword').value;

    if (username === 'frontdesk' && password === '123') {
        // 保存前台登录状态
        localStorage.setItem('frontDeskLoggedIn', 'true');
        window.location.href = '../html/frontdesk.html';
    } else {
        document.getElementById('error-message').innerText = '工号或密码错误';
    }
}

// 隐藏所有表单的函数
function hideAllForms() {
    userLoginForm.style.display = 'none';
    adminLoginForm.style.display = 'none';
    frontDeskLoginForm.style.display = 'none';
    
    // 移除所有按钮的活跃状态
    userLoginBtn.classList.remove('active');
    adminLoginBtn.classList.remove('active');
    frontDeskLoginBtn.classList.remove('active');
}

// 显示指定表单的函数
function showForm(form, button) {
    hideAllForms();
    form.style.display = 'block';
    button.classList.add('active');
}

// 添加点击事件监听器
userLoginBtn.addEventListener('click', () => {
    showForm(userLoginForm, userLoginBtn);
});

adminLoginBtn.addEventListener('click', () => {
    showForm(adminLoginForm, adminLoginBtn);
});

frontDeskLoginBtn.addEventListener('click', () => {
    showForm(frontDeskLoginForm, frontDeskLoginBtn);
});

// 添加表单提交事件监听器
userLoginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    customerLogin();
});

adminLoginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    adminLogin();
});

frontDeskLoginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    frontDeskLogin();
});

// 页面加载时隐藏所有表单
document.addEventListener('DOMContentLoaded', hideAllForms);
