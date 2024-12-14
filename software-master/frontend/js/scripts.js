// 服务器配置
const SERVER_URL = "http://127.0.0.1:8000/api/";

// 全局变量
let currentTemp = 25;
let fanSpeed = 2; // 默认中速
let isOn = false;
let targetTemp = 25;

// 检查登录状态
document.addEventListener("DOMContentLoaded", async () => {
  const currentCustomer = localStorage.getItem("currentCustomer");
  if (!currentCustomer) {
    window.location.href = "../html/login.html";
    return;
  }

  window.currentCustomer = JSON.parse(currentCustomer);

  // 显示房间号
  const roomNumberElement = document.getElementById("current-room-number");
  if (roomNumberElement) {
    roomNumberElement.textContent = window.currentCustomer.roomId;
  }

  // 获取初始空调状态
  await getACStatus();
  updateDisplayTemp();
  updateFanSpeedIcon();

  // 添加温度滑块事件监听
  const tempSlider = document.getElementById("ac-temp");
  if (tempSlider) {
    tempSlider.addEventListener("change", async () => {
      if (isOn) {
        const newTemp = parseInt(tempSlider.value);
        await setTemperature(newTemp);
      }
    });
  }

  // 添加温度输入框事件监听
  const tempInput = document.getElementById("temp-input");
  if (tempInput) {
    tempInput.addEventListener("change", async () => {
      if (isOn) {
        const newTemp = parseInt(tempInput.value);
        await setTemperature(newTemp);
      }
    });
  }
});

// 获取空调状态
async function getACStatus() {
  try {
    const response = await fetch(SERVER_URL + "ac-status/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        room_id: window.currentCustomer.roomId,
      }),
    });

    const data = await response.json();
    if (data.status === "success") {
      isOn = data.data.is_on;
      currentTemp = data.data.current_temp;
      targetTemp = data.data.target_temp || 25;
      fanSpeed = data.data.fan_speed || 2;

      // 更新界面
      updateDisplayTemp();
      updateFanSpeedIcon();

      // 更新输入框状态
      const tempInput = document.getElementById("temp-input");
      const setTempButton = tempInput.nextElementSibling;
      tempInput.disabled = !isOn;
      setTempButton.disabled = !isOn;

      if (isOn) {
        tempInput.value = targetTemp;
        document.getElementById("ac-temp").value = targetTemp;
      }
    }
  } catch (error) {
    console.error("获取空调状态失���:", error);
  }
}

// 开关机
async function togglePower() {
  try {
    const response = await fetch(SERVER_URL + "power/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        isOn: !isOn,
        room_id: window.currentCustomer.roomId,
        mode: "制冷", // 添加默认模式
      }),
    });

    const data = await response.json();
    if (data.status === "success") {
      isOn = !isOn;
      const tempInput = document.getElementById("temp-input");
      const setTempButton = tempInput.nextElementSibling;
      const fanSpeedButton = document.querySelector(
        'button[onclick="changeFanSpeed()"]'
      );

      if (isOn) {
        // 开机后启用所有控制
        tempInput.disabled = false;
        setTempButton.disabled = false;
        fanSpeedButton.disabled = false;

        // 设置默认温度和风速
        targetTemp = 25;
        fanSpeed = 2;

        // 更新显示
        await getACStatus();
      } else {
        // 关机时禁用所有控制
        tempInput.disabled = true;
        setTempButton.disabled = true;
        fanSpeedButton.disabled = true;
        document.getElementById("display-temp").textContent = "关";
      }

      // 更新界面显示
      updateDisplayTemp();
      updateFanSpeedIcon();
    }
  } catch (error) {
    console.error("开关机操作失败:", error);
    alert("开关机操作失败，请重试");
  }
}

// 设置温度
async function setTemperature(newTemp) {
  if (!isOn) {
    alert("请先开启空调");
    updateDisplayTemp(); // 恢复显示
    return;
  }

  if (!newTemp) {
    const tempInput = document.getElementById("temp-input");
    newTemp = parseInt(tempInput.value);
  }

  if (isNaN(newTemp) || newTemp < 18 || newTemp > 30) {
    alert("请输入18-30之间的温度");
    updateDisplayTemp(); // 恢复显示
    return;
  }

  try {
    const response = await fetch(SERVER_URL + "temperature/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        targetTemp: newTemp,
        room_id: window.currentCustomer.roomId,
      }),
    });

    const data = await response.json();
    if (data.status === "success") {
      targetTemp = newTemp;
      updateDisplayTemp();
      console.log(`温度已设置为: ${newTemp}°C`);
    } else {
      alert(data.message || "设置温度失败");
      updateDisplayTemp(); // 恢复显示
    }
  } catch (error) {
    console.error("设置温度失败:", error);
    alert("设置温度失败，请重试");
    updateDisplayTemp(); // 恢复显示
  }
}

// 调整风速
async function changeFanSpeed() {
  if (!isOn) {
    alert("请先开启空调");
    return;
  }

  const nextSpeed = (fanSpeed % 3) + 1; // 1->2->3->1
  console.log(`尝试设置风速为: ${nextSpeed}`);

  try {
    const response = await fetch(SERVER_URL + "fan-speed/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        fanSpeed: nextSpeed,
        room_id: window.currentCustomer.roomId,
      }),
    });

    const data = await response.json();
    if (data.status === "success") {
      fanSpeed = nextSpeed;
      updateFanSpeedIcon();
      console.log(`风速已成功调整为: ${nextSpeed}`);
    } else {
      console.error("调整风速失败:", data.message);
      alert(data.message || "调整风速失败");
    }
  } catch (error) {
    console.error("调整风速失败:", error);
    alert("调整风速失败，请重试");
  }
}

// 更新温度显示
function updateDisplayTemp() {
  const tempInput = document.getElementById("temp-input");
  const tempSlider = document.getElementById("ac-temp");
  const displayTemp = document.getElementById("display-temp");
  const currentTempDisplay = document.getElementById("current-temp");

  if (isOn) {
    displayTemp.textContent = `${targetTemp}°`;
    currentTempDisplay.textContent = `${currentTemp}°`;
    tempInput.value = targetTemp;
    tempSlider.value = targetTemp;
  } else {
    displayTemp.textContent = "关";
    tempInput.value = "";
    tempSlider.value = 25;
  }
}

// 更新风速图标
function updateFanSpeedIcon() {
  const iconElement = document.getElementById("fan-speed-icon");
  let bars = "";
  for (let i = 1; i <= 3; i++) {
    bars += `<span class="speed-bar${i <= fanSpeed ? " active" : ""}"></span>`;
  }
  iconElement.innerHTML = bars;
}

// 定期更新状态
setInterval(getACStatus, 5000); // 每5秒更新一次状态
