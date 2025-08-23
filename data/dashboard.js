// Global variables
let chart;
let currentRange = 0;
let statusUpdateInterval;
let chartUpdateInterval;

// Status color mappings
const statusColors = {
  excellent: { bg: '#f0fff4', color: '#38a169', text: 'Excellent' },
  good: { bg: '#f7fafc', color: '#4299e1', text: 'Good' },
  fair: { bg: '#fffbeb', color: '#d69e2e', text: 'Fair' },
  poor: { bg: '#fed7d7', color: '#e53e3e', text: 'Poor' }
};

// Utility functions
function getSignalStatus(rssi) {
  if (rssi > -50) return 'excellent';
  if (rssi > -60) return 'good';
  if (rssi > -70) return 'fair';
  return 'poor';
}

function getNoiseStatus(noise) {
  if (noise < -95) return 'excellent';
  if (noise < -90) return 'good';
  if (noise < -85) return 'fair';
  return 'poor';
}

function getSNRStatus(snr) {
  if (snr > 30) return 'excellent';
  if (snr > 20) return 'good';
  if (snr > 10) return 'fair';
  return 'poor';
}

function getChannelStatus(util) {
  if (util < 20) return 'excellent';
  if (util < 40) return 'good';
  if (util < 60) return 'fair';
  return 'poor';
}

function getStabilityStatus(stability) {
  if (stability > 0.8) return 'excellent';
  if (stability > 0.6) return 'good';
  if (stability > 0.4) return 'fair';
  return 'poor';
}

function updateStatusCard(elementId, value, unit, status) {
  const valueEl = document.getElementById(`${elementId}-value`);
  const statusEl = document.getElementById(`${elementId}-status`);
  
  if (valueEl) {
    valueEl.textContent = typeof value === 'number' ? value.toFixed(1) : value;
  }
  
  if (statusEl) {
    const statusInfo = statusColors[status];
    statusEl.textContent = statusInfo.text;
    statusEl.style.background = statusInfo.bg;
    statusEl.style.color = statusInfo.color;
    statusEl.className = 'card-status';
  }
}

// Chart initialization
function initChart() {
  const options = {
    series: [],
    chart: {
      type: 'line',
      height: 400,
      animations: { enabled: true, speed: 800 },
      toolbar: {
        show: true,
        tools: {
          download: true,
          selection: false,
          zoom: true,
          zoomin: true,
          zoomout: true,
          pan: false,
          reset: true
        }
      },
      zoom: { enabled: true }
    },
    dataLabels: { enabled: false },
    stroke: {
      width: [3, 3, 3, 3, 4],
      curve: 'smooth',
      dashArray: [0, 0, 0, 0, 5]
    },
    colors: ['#FF0000', '#800080', '#0000FF', '#FFA500', '#00FF00'],
    markers: {
      size: 0,
      hover: {
        size: 6
      }
    },
    xaxis: { 
      type: 'datetime',
      labels: {
        format: 'HH:mm'
      }
    },
    yaxis: [
      {
        title: { text: 'Signal Metrics (dBm, dB, %)' },
        min: -100,
        max: 100,
        labels: { formatter: val => val.toFixed(1) }
      },
      {
        opposite: true,
        title: { text: 'AI Stability (%)' },
        min: 0,
        max: 100,
        labels: { formatter: val => val.toFixed(0) + '%' }
      }
    ],
    legend: {
      position: 'top',
      horizontalAlign: 'center'
    },
    grid: {
      borderColor: '#e7e7e7',
      strokeDashArray: 5
    },
    tooltip: {
      shared: true,
      intersect: false,
      x: {
        format: 'dd/MM/yy HH:mm'
      }
    }
  };
  
  chart = new ApexCharts(document.querySelector("#chart"), options);
  chart.render();
}

// Update chart with new data
function updateChart(days) {
  currentRange = days;
  console.log(`📈 Fetching data for range: ${days} days`);

  fetch(`/history?range=${days}`)
    .then(response => response.json())
    .then(data => {
      console.log(`📊 Received ${data.length} data points`);

      // Check if data is real or demo
      if (data.length > 0) {
        const latestRecord = data[data.length - 1];
        const recordAge = Date.now() - (latestRecord.t * 1000);
        const isRecent = recordAge < 300000; // Less than 5 minutes old

        console.log(`🔍 Data Source Analysis:`);
        console.log(`   Latest record: ${new Date(latestRecord.t * 1000).toLocaleString()}`);
        console.log(`   Age: ${Math.round(recordAge / 1000)} seconds ago`);
        console.log(`   SSID: ${latestRecord.ssid || 'Unknown'}`);
        console.log(`   Status: ${isRecent ? '✅ REAL-TIME DATA' : '⚠️ OLD/DEMO DATA'}`);

        // Show data source in dashboard
        const statusText = document.getElementById('status-text');
        if (statusText && isRecent) {
          statusText.textContent += ' (Real-time data)';
        }
      }

      if (!Array.isArray(data) || data.length === 0) {
        console.log('⚠️ No data available for selected range');
        // Show empty chart with message
        const emptySeries = [
          { name: 'RSSI (dBm)', data: [], yAxisIndex: 0 },
          { name: 'Noise (dBm)', data: [], yAxisIndex: 0 },
          { name: 'SNR (dB)', data: [], yAxisIndex: 0 },
          { name: 'Channel Util (%)', data: [], yAxisIndex: 0 },
          { name: 'AI Stability (%)', data: [], yAxisIndex: 1 }
        ];
        chart.updateSeries(emptySeries);
        return;
      }

      // Simple debug - check if all data exists
      console.log('📊 First record:', data[0]);
      console.log('📊 All 5 curves data check:', {
        rssi: data[0]?.rssi,
        noise: data[0]?.noise,
        snr: data[0]?.snr,
        channel_util: data[0]?.channel_util,
        stability: data[0]?.stability
      });

      const series = [
        {
          name: 'RSSI (dBm)',
          data: data.map(d => [d.t * 1000, d.rssi || 0]),
          yAxisIndex: 0
        },
        {
          name: 'Noise (dBm)',
          data: data.map(d => [d.t * 1000, d.noise || -95]),
          yAxisIndex: 0
        },
        {
          name: 'SNR (dB)',
          data: data.map(d => [d.t * 1000, d.snr || 0]),
          yAxisIndex: 0
        },
        {
          name: 'Channel Util (%)',
          data: data.map(d => [d.t * 1000, d.channel_util || 0]),
          yAxisIndex: 0
        },
        {
          name: 'AI Stability (%)',
          data: data.map(d => [d.t * 1000, (d.stability || 0) * 100]),
          yAxisIndex: 1
        }
      ];

      // Debug: Check what noise data looks like in series
      console.log('🔍 Noise series data:', series[1].data.slice(0, 3));
      chart.updateSeries(series);
      generateAlerts(data);
    })
    .catch(error => {
      console.error('❌ Error fetching chart data:', error);
    });
}

// Update real-time status
function updateStatus() {
  fetch('/status')
    .then(response => response.json())
    .then(data => {
      // Update connection status
      const statusDot = document.getElementById('status-dot');
      const statusText = document.getElementById('status-text');

      if (data.connected) {
        statusDot.style.background = '#48bb78';
        statusText.textContent = `Connected to ${data.ssid}`;
      } else {
        statusDot.style.background = '#e53e3e';
        statusText.textContent = 'Disconnected';
      }

      // Update status cards
      updateStatusCard('rssi', data.rssi, 'dBm', getSignalStatus(data.rssi));
      updateStatusCard('noise', data.noise, 'dBm', getNoiseStatus(data.noise));
      updateStatusCard('snr', data.snr, 'dB', getSNRStatus(data.snr));
      updateStatusCard('channel', data.channel_util, '%', getChannelStatus(data.channel_util));

      // Update AI stability
      const stabilityPercent = (data.stability * 100);
      updateStatusCard('stability', stabilityPercent, '%', getStabilityStatus(data.stability));

      // Update stability bar
      const stabilityFill = document.getElementById('stability-fill');
      if (stabilityFill) {
        stabilityFill.style.width = stabilityPercent + '%';
      }
    })
    .catch(error => {
      console.error('Error fetching status:', error);
    });

  // Update AI alerts and diagnosis
  updateAIAlerts();
}

// Update AI alerts with intelligent diagnosis
function updateAIAlerts() {
  fetch('/advanced-ai')
    .then(response => response.json())
    .then(data => {
      updateCurrentAIAlert(data);
    })
    .catch(error => {
      console.error('Error fetching AI data:', error);
    });
}

// Update the current AI alert card with diagnosis and solutions
function updateCurrentAIAlert(aiData) {
  const alertCard = document.getElementById('current-ai-alert');
  const alertIcon = document.getElementById('alert-icon');
  const alertTitle = document.getElementById('alert-title');
  const alertConfidence = document.getElementById('alert-confidence');
  const alertMessage = document.getElementById('alert-message');
  const alertSolution = document.getElementById('alert-solution');

  if (!alertCard) return;

  // Update alert type styling
  alertCard.className = `ai-alert-card ${aiData.alert_type}`;

  // Update alert content
  const alertIcons = {
    'interference': '📡',
    'weak_signal': '📶',
    'degrading': '📉',
    'congestion': '🚦',
    'unstable': '⚡',
    'excellent': '✅',
    'good': '👍',
    'poor': '⚠️',
    'unknown': '🔍'
  };

  alertIcon.textContent = alertIcons[aiData.alert_type] || '🔍';
  alertTitle.textContent = getAlertTitle(aiData.alert_type);
  alertConfidence.textContent = `${(aiData.confidence * 100).toFixed(0)}% confidence`;
  alertMessage.textContent = aiData.alert_message;

  // Generate AI solutions
  const solutions = generateAISolutions(aiData);
  alertSolution.innerHTML = solutions;
}

// Get human-readable alert titles
function getAlertTitle(alertType) {
  const titles = {
    'interference': 'Interference Detected',
    'weak_signal': 'Weak Signal Strength',
    'degrading': 'Signal Degrading',
    'congestion': 'Network Congestion',
    'unstable': 'Unstable Connection',
    'excellent': 'Excellent Connection',
    'good': 'Good Connection Quality',
    'poor': 'Poor Connection Quality',
    'unknown': 'Analyzing Connection'
  };
  return titles[alertType] || 'Connection Analysis';
}

// Generate AI-powered solutions based on the problem type
function generateAISolutions(aiData) {
  const solutions = {
    'interference': `
      <h4>🔧 Recommended Solutions:</h4>
      <ul>
        <li>Move closer to your WiFi router to improve signal strength</li>
        <li>Check for interfering devices (microwaves, baby monitors, Bluetooth devices)</li>
        <li>Switch to a less congested WiFi channel (try channels 1, 6, or 11 for 2.4GHz)</li>
        <li>Consider upgrading to 5GHz band if available</li>
      </ul>
    `,
    'weak_signal': `
      <h4>🔧 Recommended Solutions:</h4>
      <ul>
        <li>Move closer to your WiFi router or access point</li>
        <li>Remove physical obstacles between device and router</li>
        <li>Check if router antennas are properly positioned</li>
        <li>Consider installing a WiFi extender or mesh system</li>
      </ul>
    `,
    'degrading': `
      <h4>🔧 Recommended Solutions:</h4>
      <ul>
        <li>Check for new obstacles or interference sources</li>
        <li>Restart your WiFi router to refresh the connection</li>
        <li>Update your device's WiFi drivers</li>
        <li>Monitor for patterns - degradation may be temporary</li>
      </ul>
    `,
    'congestion': `
      <h4>🔧 Recommended Solutions:</h4>
      <ul>
        <li>Switch to a less crowded WiFi channel</li>
        <li>Upgrade to 5GHz band to avoid 2.4GHz congestion</li>
        <li>Limit bandwidth-heavy activities during peak hours</li>
        <li>Consider Quality of Service (QoS) settings on your router</li>
      </ul>
    `,
    'unstable': `
      <h4>🔧 Recommended Solutions:</h4>
      <ul>
        <li>Check for intermittent interference sources</li>
        <li>Ensure router firmware is up to date</li>
        <li>Try changing WiFi channel to avoid interference</li>
        <li>Monitor connection during different times of day</li>
      </ul>
    `,
    'excellent': `
      <h4>✨ Connection Status:</h4>
      <ul>
        <li>Your WiFi connection is performing excellently</li>
        <li>Signal strength and quality are optimal</li>
        <li>No immediate action required</li>
        <li>Continue monitoring for any changes</li>
      </ul>
    `,
    'good': `
      <h4>👍 Connection Status:</h4>
      <ul>
        <li>Your WiFi connection is performing well</li>
        <li>Minor optimizations possible but not critical</li>
        <li>Monitor for any degradation trends</li>
        <li>Consider optimizations during maintenance windows</li>
      </ul>
    `
  };

  return solutions[aiData.alert_type] || `
    <h4>🔍 Analysis in Progress:</h4>
    <ul>
      <li>AI is analyzing your connection patterns</li>
      <li>Collecting data for accurate diagnosis</li>
      <li>Check back in a few moments for detailed insights</li>
    </ul>
  `;
}

// Generate alerts based on current data
function generateAlerts(data) {
  const alertsContainer = document.getElementById('alerts-container');
  if (!alertsContainer || !data || data.length === 0) return;
  
  alertsContainer.innerHTML = '';
  const latestData = data[data.length - 1];
  
  // Check for various alert conditions
  const alerts = [];
  
  if (latestData.rssi < -80) {
    alerts.push({
      type: 'error',
      icon: '⚠️',
      message: 'Weak signal strength detected. Consider moving closer to the router.'
    });
  }
  
  if (latestData.snr < 10) {
    alerts.push({
      type: 'warning',
      icon: '📶',
      message: 'Low signal quality. Network interference may be present.'
    });
  }
  
  if (latestData.channel_util > 70) {
    alerts.push({
      type: 'warning',
      icon: '🌐',
      message: 'High channel utilization. Network congestion detected.'
    });
  }
  
  if (latestData.stability < 0.5) {
    alerts.push({
      type: 'error',
      icon: '🤖',
      message: 'AI predicts unstable connection. Consider troubleshooting.'
    });
  } else if (latestData.stability > 0.8) {
    alerts.push({
      type: 'success',
      icon: '✅',
      message: 'Excellent connection stability predicted by AI.'
    });
  }
  
  // Add alerts to container
  if (alerts.length === 0) {
    alertsContainer.innerHTML = '<div class="alert info"><span>📊</span> All systems operating normally.</div>';
  } else {
    alerts.forEach(alert => {
      const alertDiv = document.createElement('div');
      alertDiv.className = `alert ${alert.type}`;
      alertDiv.innerHTML = `<span>${alert.icon}</span> ${alert.message}`;
      alertsContainer.appendChild(alertDiv);
    });
  }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
  console.log('Dashboard initializing...');
  
  // Initialize chart
  initChart();
  
  // Load initial data (today)
  updateChart(0);
  updateStatus();
  
  // Setup time range buttons
  document.querySelectorAll('.time-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const days = parseInt(btn.dataset.days);
      
      // Update active button
      document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      // Update chart
      updateChart(days);
    });
  });
  
  // Start periodic updates
  statusUpdateInterval = setInterval(updateStatus, 5000); // Every 5 seconds
  chartUpdateInterval = setInterval(() => {
    if (currentRange === 0) { // Only auto-update for "Today" view
      updateChart(currentRange);
    }
  }, 30000); // Every 30 seconds
  
  console.log('Dashboard initialized successfully');
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  if (statusUpdateInterval) clearInterval(statusUpdateInterval);
  if (chartUpdateInterval) clearInterval(chartUpdateInterval);
});
