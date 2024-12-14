let defaultTemp = 24;
let fanSpeed = 1; // 0 代表关闭，1,2,3 代表低中高风速
let isOn = false;
let targetTemp = 24;
let currentTemp = 24;
let pollingInterval = null;
let roomId = 1;
let pollingErrorCount = 0;
// 添加服务器地址配置
const SERVER_URL = "http://127.0.0.1:8000/"; // 这里需要替换为您的Django服务器地址

// 添加 API 对象定义
const api = {
  async getRoomsStatus(roomId) {
    //
    const response = await fetch("http://127.0.0.1:8000/api/room_status/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ room_id:roomId, }),
    });
    return response.json();
  },
  async postSetTemperature(data) {
    const response = await fetch(SERVER_URL + "api/temperature/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        targetTemp: data.temperature,
        room_id: roomId,
      }),
    });
    return response.json();
  },

  async postTurnOn(data) {
    const response = await fetch(SERVER_URL + "api/power/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        isOn: true,
        room_id: roomId,
      }),
    });
    return response.json();
  },

  async postTurnOff(data) {
    const response = await fetch(SERVER_URL + "api/power/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        isOn: false,
        room_id: roomId,
      }),
    });
    return response.json();
  },

  async postSetSpeed(data) {
    const response = await fetch(SERVER_URL + "api/fan-speed/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        fanSpeed: data.speed,
        room_id: roomId,
      }),
    });
    return response.json();
  },
};

// 添加错误处理函数
function showError(message) {
  alert(message);
}

// 修改 sendToServer 函数
async function sendToServer(action, data) {
  try {
    let response;
    switch (action) {
      case "tempSlider":
        response = await api.postSetTemperature({
          temperature: data.temperature,
        });
        break;
      case "togglePower":
        response = data.isOn
          ? await api.postTurnOn(data)
          : await api.postTurnOff(data);
        break;
      case "changeFanSpeed":
        response = await api.postSetSpeed({
          speed: data.speed,
        });
        break;


    }
    if (response && response.status === "error") {
      showError(response.message);
    }
  } catch (error) {
    console.error("发送请求失败:", error);
    showError("连接服务器失败，请检查网络连接");
  }
}
function setRoomId(newRoomId) {
  roomId = parseInt(newRoomId, 10); // 10 表示按十进制解析
  console.log(`房间 ID 已更新为: ${roomId}`);
}
function setTemperature() {
  if (!isOn) return;

  const tempInput = document.getElementById("temp-input");
  const newTemp = parseInt(tempInput.value);

  if (newTemp < 18 || newTemp > 30) {
    alert("温度必须在18-30度之间");
    tempInput.value = defaultTemp;
    return;
  }

  sendToServer("tempSlider", { temperature: newTemp });
  targetTemp = newTemp;
  updateDisplayTemp();
}

function togglePower() {
  isOn = !isOn;
  const tempInput = document.getElementById("temp-input");
  const setTempButton = tempInput.nextElementSibling;

  if (isOn) {
    document.getElementById("current-temp").value = currentTemp;
    document.getElementById("display-temp").value = targetTemp;
    tempInput.disabled = false;
    setTempButton.disabled = false;
    updateDisplayTemp();
  } else {
    document.getElementById("display-temp").textContent = "关";
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


// 滑动条变化时更新显示温度
document.getElementById("ac-temp").addEventListener("input", function () {
  if (isOn) {
    currentTemp = parseInt(this.value, 10);
    updateDisplayTemp();
    sendToServer("tempSlider", { temperature: currentTemp });
  }
});


function startPolling(interval = 5000) {
  stopPolling();
  pollingInterval = setInterval(async () => {
    try {
      const response = await api.getRoomsStatus(roomId);
      if (response && response.status === "success") {
        pollingErrorCount = 0;
        updateRoomState(response.data);
      } else {
        console.error("获取房间状态失败:", response.message);
        pollingErrorCount++;
      }
    } catch (error) {
      console.error("轮询请求失败:", error);
      pollingErrorCount++;
      showError("无法连接到服务器，请检查网络。");
    }

    if (pollingErrorCount >= 5) {
      stopPolling();
      showError("轮询失败次数过多，已停止轮询。请检查网络或服务器。");
      setTimeout(() => {
        pollingErrorCount = 0;
        startPolling(interval); // 尝试重新启动轮询
      }, 5000);
    }
  }, interval);
}
// 1111111111111111111111111111111111111111111111111111暂停轮询
function stopPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
}
// 22222222222222222222222222222222222222222222222222222222更新状态
function updateRoomState(data) {
  if (!data) return;

  isOn = data.isOn1;
  togglePowerUI(isOn);

  targetTemp = data.targetTemp
  currentTemp = data.currentTemp;
  updateDisplayTemp();

  fanSpeed = data.fanSpeed;
  updateFanSpeedIcon();
}
function updateDisplayTemp() {
  if (isOn) {
    const tempElement1 = document.getElementById("display-temp");
    const tempElement2 = document.getElementById("current-temp");
    tempElement1.textContent = `${targetTemp}°`;
    tempElement2.textContent = `${currentTemp}°`;
    //document.getElementById("current-temp").value = currentTemp;
    document.getElementById("temp-input").value = targetTemp;
    //document.getElementById("display-temp").value = targetTemp;
    //document.getElementById("display-input").value = targetTemp;
  }
}
function togglePowerUI(isOn) {
  const tempInput = document.getElementById("temp-input");
  const setTempButton = tempInput.nextElementSibling;
  const displayTemp = document.getElementById("display-temp");

  if (isOn) {
    tempInput.disabled = false;
    setTempButton.disabled = false;
    displayTemp.textContent = `${targetTemp}°`;
  } else {
    tempInput.disabled = true;
    setTempButton.disabled = true;
    displayTemp.textContent = "关";
  }
  }
function updateFanSpeedIcon() {
  const iconElement = document.getElementById("fan-speed-icon");

  let bars = "";
  for (let i = 1; i <= 3; i++) {
    bars += `<span class="speed-bar${i <= fanSpeed ? " active" : ""}"></span>`;
  }
  iconElement.innerHTML = bars;
}
document.addEventListener("DOMContentLoaded", async () => {
  const response = await api.getRoomsStatus(roomId);
  if (response && response.status === "success") {
    updateRoomState(response.data);
  }
  startPolling(5000);

});

 页面关闭时停止轮询
window.addEventListener("beforeunload", () => {
  stopPolling();
});