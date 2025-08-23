// UI references
const wifiList = document.getElementById('wifiList');
const wifiPass = document.getElementById('wifiPass');
const connectBtn = document.getElementById('connectBtn');
const connStatus = document.getElementById('connStatus');
const liveToggle = document.getElementById('liveToggle');
const loadHistory = document.getElementById('loadHistory');
const downloadCSV = document.getElementById('downloadCSV');
const clearHistory = document.getElementById('clearHistory');
const message = document.getElementById('message');
const analyzeBtn = document.getElementById('analyzeBtn');
const aiServerInput = document.getElementById('aiServer');

let chart = null;
let liveTimer = null;
let seriesData = []; // [ [timestamp, value], ... ]
let annotationX = [];

// helper
async function httpGetJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error('HTTP '+r.status);
  return await r.json();
}
async function httpPostJSON(url, obj) {
  const r = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(obj)});
  if (!r.ok) throw new Error('HTTP '+r.status);
  return await r.json();
}
async function httpPostForm(url, formObj) {
  const body = new URLSearchParams(formObj);
  const r = await fetch(url, {method:'POST', body});
  if (!r.ok) throw new Error('HTTP '+r.status);
  return await r.json();
}

// populate WiFi list
async function scanWifi(){
  try {
    const nets = await httpGetJSON('/scan');
    wifiList.innerHTML = '';
    nets.forEach(n => {
      const opt = document.createElement('option');
      opt.value = n.ssid;
      opt.textContent = `${n.ssid}  —  ${n.rssi} dBm`;
      wifiList.appendChild(opt);
    });
    connStatus.textContent = 'Select network and connect';
  } catch(err) {
    connStatus.textContent = 'Scan failed';
    console.error(err);
  }
}

// connect
connectBtn.onclick = async () => {
  const ssid = wifiList.value;
  const pass = wifiPass.value || '';
  if (!ssid) return alert('Select an SSID');
  connStatus.textContent = 'Connecting...';
  try {
    // prefer JSON body
    const res = await httpPostJSON('/connect', { ssid, pass });
    if (res.status === 'connected' || res.ip) {
      connStatus.textContent = 'Connected: ' + (res.ip || 'OK');
      startLive();
    } else if (res.status === 'failed') {
      connStatus.textContent = 'Connection failed';
    } else {
      connStatus.textContent = JSON.stringify(res);
    }
  } catch(e) {
    // try form fallback
    try {
      const res = await httpPostForm('/connect', { ssid, pass });
      connStatus.textContent = res.status === 'connected' ? 'Connected' : 'Failed';
      startLive();
    } catch(err){
      connStatus.textContent = 'Connect error';
      console.error(err);
    }
  }
};

// chart init
async function initChart(){
  const options = {
    chart: { type: 'line', height: 420, animations: { enabled: true }},
    series: [{ name: 'RSSI (dBm)', data: [] }],
    xaxis: { type: 'datetime' },
    yaxis: { opposite: false },
    stroke: { curve: 'smooth' },
    markers: { size: 3 },
    annotations: { xaxis: [] }
  };
  chart = new ApexCharts(document.querySelector('#chart'), options);
  await chart.render();
}

// live fetch
async function fetchLivePoint() {
  try {
    const d = await httpGetJSON('/live');
    const t = new Date(d.t).getTime();
    const v = Number(d.rssi);
    seriesData.push([t, v]);
    if (seriesData.length > 2000) seriesData.shift();
    await chart.updateSeries([{ name:'RSSI (dBm)', data: seriesData }], true);
  } catch(e){
    console.error('live fetch error', e);
  }
}

// start/stop live
function startLive() {
  if (liveTimer) clearInterval(liveTimer);
  liveTimer = setInterval(fetchLivePoint, 3000); // poll every 3s
  fetchLivePoint();
  liveToggle.textContent = 'Stop Live';
  message.textContent = 'Live plotting...';
}
function stopLive() {
  if (liveTimer) clearInterval(liveTimer);
  liveTimer = null;
  liveToggle.textContent = 'Start Live';
  message.textContent = 'Live stopped';
}
liveToggle.onclick = () => {
  if (liveTimer) stopLive(); else startLive();
};

// load history
loadHistory.onclick = async () => {
  try {
    const data = await httpGetJSON('/history');
    seriesData = data.map(r => [ new Date(r.t).getTime(), Number(r.rssi) ]);
    await chart.updateSeries([{ name:'RSSI (dBm)', data: seriesData }], true);
    message.textContent = `Loaded ${seriesData.length} points`;
  } catch (e) {
    message.textContent = 'History load failed';
    console.error(e);
  }
};

// download csv action
downloadCSV.onclick = () => {
  window.location.href = '/download';
};

// clear history
clearHistory.onclick = async () => {
  if (!confirm('Clear history on device?')) return;
  try {
    const r = await fetch('/clear', {method:'POST'});
    message.textContent = r.ok ? 'History cleared' : 'Clear failed';
    seriesData = [];
    chart.updateSeries([{ name:'RSSI (dBm)', data: [] }]);
  } catch(e){
    message.textContent = 'Clear failed';
  }
};

// analyze via AI server
analyzeBtn.onclick = async () => {
  const aiUrl = (aiServerInput.value || '').trim();
  if (!aiUrl) return alert('Enter AI server URL (ex: http://192.168.1.50:8000)');
  message.textContent = 'Analyzing...';
  try {
    const payload = { esp_host: window.location.origin, limit: 2000, contamination: 0.02 };
    const res = await fetch( aiUrl.replace(/\/$/,'') + '/analyze', {
      method:'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('AI server '+res.status);
    const ans = await res.json();
    const anomalies = ans.anomalies || [];
    // create x-axis annotations
    const ann = anomalies.map(a => ({ x: new Date(a.t).getTime(), borderColor:'red', label:{text:`Anomaly ${a.rssi}`}}));
    chart.updateOptions({ annotations: { xaxis: ann } });
    message.textContent = `Analysis done: ${anomalies.length} anomalies`;
  } catch(e) {
    message.textContent = 'AI analyze failed';
    console.error(e);
  }
};

// initial load
window.addEventListener('load', async () => {
  await initChart();
  await scanAndInit();
});

async function scanAndInit(){
  await scanWifi();
  // auto-start live plotting (will fetch /live successfully if available)
  try {
    const status = await httpGetJSON('/status');
    if (status && status.sta_connected) startLive();
    else startLive(); // still start live from AP even if not connected
  } catch(e){
    startLive();
  }
}
