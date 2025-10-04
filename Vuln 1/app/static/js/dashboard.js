document.addEventListener("DOMContentLoaded", ()=> {
  const deviceListEl = document.getElementById("device-list");
  const incidentLog = document.getElementById("incident-log");
  const simLog = document.getElementById("sim-log");
  const tokenInput = document.getElementById("token");
  const opForm = document.getElementById("op-form");
  const targetEl = document.getElementById("target");
  const opResult = document.getElementById("op-result");

  // Адмін-панель елементи
  const adminTokenInput = document.getElementById("admin-token");
  const adminResult = document.getElementById("admin-result");
  const insertAdminBtn = document.getElementById("insert-admin-key");
  const adminButtons = document.querySelectorAll(".admin-btn");
  const adminCommandsEl = document.querySelector('.admin-commands');

  // Нові елементи управління
  const powerSlider = document.getElementById("powerSlider");
  const powerValue = document.getElementById("powerValue");
  const voltageSlider = document.getElementById("voltageSlider");
  const voltageValue = document.getElementById("voltageValue");

  let devices = window.START_DEVICES || [];
  let controlPanelOpen = false;

  // Ініціалізація графіків (Chart.js)
  const loadCtx = document.getElementById("loadChart").getContext("2d");
  const statusCtx = document.getElementById("statusChart").getContext("2d");
  const powerCtx = document.getElementById("powerChart").getContext("2d");
  const tempCtx = document.getElementById("tempChart").getContext("2d");
  
  let loadChart = new Chart(loadCtx, {
    type: 'line',
    data: {
      labels: devices.map(d=>d.name),
      datasets: [{
        label: 'Навантаження',
        data: devices.map(d=>d.load),
        fill: true,
        tension: 0.3
      }]
    },
    options: {animation:false, plugins:{legend:{display:false}}, scales:{y:{min:0,max:120}}}
  });
  
  let statusChart = new Chart(statusCtx, {
    type: 'doughnut',
    data: {
      labels: ['OK', 'WARNING', 'OFFLINE', 'DEGRADED', 'COMPROMISED'],
      datasets: [{
        data: [0, 0, 0, 0, 0]
      }]
    },
    options: {animation:false, plugins:{legend:{display:true}}}
  });
  
  let powerChart = new Chart(powerCtx, {
    type: 'bar',
    data: {
      labels: devices.map(d=>d.name),
      datasets: [{
        label: 'Потужність',
        data: devices.map(d=>d.power_level || 75),
      }]
    },
    options: {animation:false, plugins:{legend:{display:false}}, scales:{y:{min:0,max:100}}}
  });
  
  let tempChart = new Chart(tempCtx, {
    type: 'line',
    data: {
      labels: devices.map(d=>d.name),
      datasets: [{
        label: 'Температура',
        data: devices.map(d=>d.temperature || 35),
        fill: true,
        tension: 0.3
      }]
    },
    options: {animation:false, plugins:{legend:{display:false}}, scales:{y:{min:0,max:80}}}
  });

  function renderDeviceList(devs){
    deviceListEl.innerHTML = "";
    devs.forEach(d=>{
      const li = document.createElement("li");
      li.className = "device";
      li.dataset.id = d.id;
      li.innerHTML = `
        <div class="title">${d.name}</div>
        <div class="meta">${d.kind} • Роль: ${d.role} • Локація: ${d.location}</div>
        <div class="status-row">
          <div>Статус: <span class="status ${d.status}">${d.status}</span></div>
          <div class="load">Навантаження: <span class="loadval">${d.load}</span>%</div>
        </div>
        <div class="extra" id="extra-${d.id}"></div>
      `;
      deviceListEl.appendChild(li);
      const extraEl = li.querySelector(`#extra-${d.id}`);
      if (d.extra && Object.keys(d.extra).length){
        Object.entries(d.extra).forEach(([k,v])=>{
          const kv = document.createElement("div");
          kv.className = "kv";
          kv.innerHTML = `<b>${k}:</b> ${v}`;
          extraEl.appendChild(kv);
        });
      }
    });
  }

  function refreshUI(newDevices){
    devices = newDevices;
    renderDeviceList(devices);
    
    // Оновлення графіків
    loadChart.data.labels = devices.map(d=>d.name);
    loadChart.data.datasets[0].data = devices.map(d=>d.load);
    loadChart.update();
    
    // Статистика статусів
    const statusCount = {
      'OK': 0, 'WARNING': 0, 'OFFLINE': 0, 'DEGRADED': 0, 'COMPROMISED': 0
    };
    
    devices.forEach(d => {
      statusCount[d.status] = (statusCount[d.status] || 0) + 1;
    });
    
    statusChart.data.datasets[0].data = [
      statusCount.OK, statusCount.WARNING, statusCount.OFFLINE,
      statusCount.DEGRADED, statusCount.COMPROMISED
    ];
    statusChart.update();
    
    powerChart.data.labels = devices.map(d=>d.name);
    powerChart.data.datasets[0].data = devices.map(d=>d.power_level || 75);
    powerChart.update();
    
    tempChart.data.labels = devices.map(d=>d.name);
    tempChart.data.datasets[0].data = devices.map(d=>d.temperature || 35);
    tempChart.update();
  }

  async function fetchDevices(){
    try{
      const r = await fetch("/api/devices");
      const j = await r.json();
      refreshUI(j.devices);
    }catch(e){
      console.error(e);
    }
  }

  setInterval(fetchDevices, 2500);
  fetchDevices();

  // Функція показу сповіщень
  function showAlert(message, level = 'warning') {
      const alertDiv = document.createElement('div');
      alertDiv.className = `alert alert-${level}`;
      alertDiv.innerHTML = `
          <div class="alert-content">
              <span class="alert-close">&times;</span>
              <h3>${level === 'danger' ? '⚠️ КРИТИЧНА ПОДІЯ' : 'УВАГА'}</h3>
              <p>${message}</p>
          </div>
      `;
      
      document.body.appendChild(alertDiv);
      
      // Автоматичне приховування через 10 секунд
      setTimeout(() => {
          alertDiv.remove();
      }, 10000);
      
      // Закриття по кліку
      alertDiv.querySelector('.alert-close').addEventListener('click', () => {
          alertDiv.remove();
      });
  }

  // Оперативна панель: тепер спочатку перевіряємо token та відкриваємо/закриваємо панель управління
  opForm.addEventListener("submit", async (ev)=>{
    ev.preventDefault();
    const token = tokenInput.value.trim();
    if (!token) { opResult.textContent = "Потрібен ключ управління"; return; }

    try{
      const r = await fetch('/api/validate_token', {
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + token }
      });
      if (!r.ok) {
        const jj = await r.json().catch(()=>({detail:'invalid'}));
        opResult.textContent = jj.detail || 'Токен не пройшов перевірку';
        return;
      }

      // toggle panel
      controlPanelOpen = !controlPanelOpen;
      const sliders = document.getElementById('control-sliders');
      const submitBtn = document.getElementById('op-submit');
      if (controlPanelOpen) {
        sliders.style.display = 'block';
        submitBtn.textContent = 'Закрити панель управління';
        tokenInput.readOnly = true;
        targetEl.disabled = false;
        opResult.textContent = 'Доступ відкрито — виберіть пристрій.';
      } else {
        sliders.style.display = 'none';
        submitBtn.textContent = 'Відкрити панель управління';
        tokenInput.readOnly = false;
        targetEl.disabled = true;
        opResult.textContent = 'Доступ закрито.';
      }

    }catch(e){
      opResult.textContent = 'Помилка: ' + e.message;
    }
  });

  // при виборі пристрою — заповнюємо повзунки поточними значеннями
  targetEl.addEventListener('change', ()=>{
    const target = targetEl.value;
    if (!target) return;
    const dev = devices.find(d => d.id === target);
    if (!dev) return;
    document.getElementById('control-sliders').style.display = 'block';
    powerSlider.value = dev.power_level || 75;
    powerValue.textContent = powerSlider.value + '%';
    voltageSlider.value = dev.voltage || 50;
    voltageValue.textContent = voltageSlider.value + '%';
  });

  // локальне оновлення графіків при русі повзунків
  powerSlider.addEventListener("input", () => {
    powerValue.textContent = powerSlider.value + "%";
    const target = targetEl.value;
    if (!target) return;
    const idx = devices.findIndex(d => d.id === target);
    if (idx >= 0) {
      powerChart.data.datasets[0].data[idx] = parseInt(powerSlider.value);
      powerChart.update();
    }
  });

  powerSlider.addEventListener("change", async () => {
    const token = tokenInput.value.trim();
    const target = targetEl.value;
    if (!token) { showAlert("Для регулювання потужності потрібен ключ управління", "warning"); return; }
    if (!target) { showAlert("Виберіть пристрій", "warning"); return; }

    try {
      const body = JSON.stringify({
        device_id: target,
        power_level: parseInt(powerSlider.value)
      });
      const r = await fetch("/api/adjust_power", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token
        },
        body
      });
      const j = await r.json();
      incidentLog.innerHTML = `<div>${new Date().toLocaleString()} • ${j.message}</div>` + incidentLog.innerHTML;
      await fetchDevices();
    } catch(e) {
      showAlert("Помилка регулювання потужності: " + e.message, "danger");
    }
  });

  voltageSlider.addEventListener("input", () => {
    voltageValue.textContent = voltageSlider.value + "%";
    const target = targetEl.value;
    if (!target) return;
    const idx = devices.findIndex(d => d.id === target);
    if (idx >= 0) {
      // тимчасово зробимо невелику кореляцію: змінюємо tempChart трохи
      tempChart.data.datasets[0].data[idx] = Math.max(0, parseInt(20 + (voltageSlider.value/100)*60));
      tempChart.update();
    }
  });

  voltageSlider.addEventListener("change", async () => {
    const token = tokenInput.value.trim();
    const target = targetEl.value;
    if (!token) { showAlert("Для регулювання напруги потрібен ключ управління", "warning"); return; }
    if (!target) { showAlert("Виберіть пристрій", "warning"); return; }

    try {
      const body = JSON.stringify({
        device_id: target,
        voltage: parseInt(voltageSlider.value)
      });
      const r = await fetch("/api/adjust_voltage", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token
        },
        body
      });
      const j = await r.json();
      incidentLog.innerHTML = `<div>${new Date().toLocaleString()} • ${j.message}</div>` + incidentLog.innerHTML;
      await fetchDevices();
    } catch(e) {
      showAlert("Помилка регулювання напруги: " + e.message, "danger");
    }
  });

  // Вставка адмін-ключа (в UI — тільки поле та кнопка). Перевіряємо його на сервері та розблоковуємо кнопки
  insertAdminBtn.addEventListener('click', async () => {
    const token = adminTokenInput.value.trim();
    if (!token) { adminResult.textContent = 'Введіть ключ адміністратора'; return; }
    try{
      const r = await fetch('/api/admin/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ admin_token: token })
      });
      if (!r.ok) {
        adminResult.textContent = 'Ключ не прийнято';
        return;
      }
      const j = await r.json();
      adminResult.textContent = 'Ключ адміністратора прийнято — кнопки розблоковано';
      adminTokenInput.readOnly = true;
      // розблоковуємо кнопки
      adminCommandsEl.style.pointerEvents = 'auto';
      adminCommandsEl.style.opacity = '1';

    }catch(e){
      adminResult.textContent = 'Помилка: ' + e.message;
    }
  });

  // Обробники для адмін-панелі
  adminButtons.forEach(btn => {
    btn.addEventListener("click", async () => {
      const command = btn.dataset.command;
      const token = adminTokenInput.value.trim();
      if (!token) { adminResult.textContent = "Введіть ключ адміністратора"; return; }
      if (!confirm(`ВИ ВПЕВНЕНІ? Ця дія: ${command.toUpperCase()}!`)) { return; }
      try {
        const body = JSON.stringify({
          command: command,
          admin_token: token
        });
        const r = await fetch("/api/admin/control", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body
        });
        const j = await r.json();
        adminResult.textContent = j.message || JSON.stringify(j);
        if (j.alert) { showAlert(j.alert, "danger"); }
        incidentLog.innerHTML = `<div>${new Date().toLocaleString()} • [admin] ${j.message}</div>` + incidentLog.innerHTML;
        await fetchDevices();
      } catch(e) {
        adminResult.textContent = "Помилка: " + e.message;
      }
    });
  });

});
