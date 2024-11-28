let currentTemp = 25;
let fanSpeed = 1; // 1, 2, 3 - 代表低、中、高风速
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
    if (isOn) {
        document.getElementById('ac-temp').value = currentTemp;
        updateDisplayTemp();
    } else {
        document.getElementById('display-temp').textContent = '关';
    }
}

function changeFanSpeed() {
    if (isOn) {
        fanSpeed = (fanSpeed % 3) + 1;
        updateFanSpeedIcon();
    }
}

function updateDisplayTemp() {
    if (isOn) {
        const tempElement = document.getElementById('display-temp');
        tempElement.textContent = `${currentTemp}°`;
        document.getElementById('ac-temp').value = currentTemp;
    }
}

function updateFanSpeedIcon() {
    const iconElement = document.getElementById('fan-speed-icon');
    switch (fanSpeed) {
        case 1:
            iconElement.innerHTML = '&#9734;&#9734;&#9734;';
            break;
        case 2:
            iconElement.innerHTML = '&#9733;&#9734;&#9734;';
            break;
        case 3:
            iconElement.innerHTML = '&#9733;&#9733;&#9733;';
            break;
    }
}

// 其他代码...

// 示例数据：每天的花费
const labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
const data = [100, 120, 90, 150, 130, 110, 140];

// 获取canvas元素
const ctx = document.getElementById('expense-chart').getContext('2d');

// 创建图表
const expenseChart = new Chart(ctx, {
    type: 'bar', // 图表类型，可以是'bar', 'line', 'pie'等
    data: {
        labels: labels,
        datasets: [{
            label: '每日花费',
            data: data,
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)',
                'rgba(255, 99, 132, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)',
                'rgba(255, 99, 132, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// 其他代码...

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