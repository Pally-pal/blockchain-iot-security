// IoT Blockchain Security Frontend - JavaScript
// API client and UI handler

const config = {
    apiHost: localStorage.getItem('apiHost') || 'https://blockchain-iot-security-1.onrender.com',
    apiPort: localStorage.getItem('apiPort') || '',
    autoRefresh: true,
    refreshInterval: 30000
};

function getApiUrl() {
    if (config.apiPort) {
        return `${config.apiHost}:${config.apiPort}`;
    }
    return config.apiHost;
}

document.addEventListener('DOMContentLoaded', () => {
    updateApiBaseUrl();
    loadDashboard();
    setupEventListeners();
    setupAutoRefresh();
});

function setupEventListeners() {
    document.getElementById('registerForm')?.addEventListener('submit', handleRegister);
    setTimeout(() => addSensorReading(), 100);
    document.getElementById('verifyForm')?.addEventListener('submit', handleVerify);
    document.getElementById('verifyJsonInput')?.addEventListener('change', () => {
        document.getElementById('verifyHash').value = '';
    });
    document.getElementById('verifyDeviceForm')?.addEventListener('submit', handleVerifyDevice);
    document.getElementById('hashForm')?.addEventListener('submit', handleHash);
    document.getElementById('settingsForm')?.addEventListener('change', updateApiBaseUrl);
}

function updateApiBaseUrl() {
    const host = document.getElementById('apiHost')?.value || config.apiHost;
    const port = document.getElementById('apiPort')?.value || config.apiPort;
    const url = port ? `${host}:${port}` : host;
    const el = document.getElementById('apiBaseUrl');
    if (el) el.textContent = url;
}

function saveSettings() {
    const host = document.getElementById('apiHost').value;
    const port = document.getElementById('apiPort').value;
    localStorage.setItem('apiHost', host);
    localStorage.setItem('apiPort', port);
    config.apiHost = host;
    config.apiPort = port;
    updateApiBaseUrl();
    showAlert('Settings saved successfully!', 'success');
    const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
    modal?.hide();
    location.reload();
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    document.getElementById('alertContainer').appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
}

function switchTab(tabId) {
    const tab = bootstrap.Tab.getOrCreateInstance(document.getElementById(tabId));
    tab.show();
}

// DASHBOARD

function loadDashboard() {
    refreshDashboard();
    loadStatistics();
}

function refreshDashboard() {
    Promise.all([
        loadHealth(),
        loadTotalRecords(),
        loadStatistics()
    ]).catch(error => {
        console.error('Dashboard load error:', error);
        updateHealthStatus('unhealthy');
    });
}

async function loadHealth() {
    try {
        const response = await fetch(`${getApiUrl()}/api/health`);
        const data = await response.json();
        if (data.status === 'healthy') {
            updateHealthStatus('healthy');
            document.getElementById('dashboardBalance').textContent = data.account_balance;
            document.getElementById('dashboardRecords').textContent = data.total_records;
            document.getElementById('dashboardNetwork').textContent = 'Connected';
            document.getElementById('dashboardTimestamp').textContent = new Date(data.timestamp).toLocaleString();
            document.getElementById('infoContractAddr').textContent = data.contract_address;
            document.getElementById('infoAccountAddr').textContent = data.account_address;
            document.getElementById('infoBlockchainUrl').textContent = data.network;
            document.getElementById('infoApiStatus').innerHTML = '<span class="badge bg-success">Active</span>';
        } else {
            updateHealthStatus('unhealthy');
        }
    } catch (error) {
        console.error('Health check error:', error);
        updateHealthStatus('unhealthy');
        document.getElementById('dashboardNetwork').textContent = 'Disconnected';
    }
}

function updateHealthStatus(status) {
    const statusBadge = document.getElementById('healthStatus');
    if (status === 'healthy') {
        statusBadge.innerHTML = '<span class="badge bg-success"><span class="status-indicator healthy"></span>System Healthy</span>';
    } else {
        statusBadge.innerHTML = '<span class="badge bg-danger"><span class="status-indicator unhealthy"></span>System Error</span>';
    }
}

async function loadTotalRecords() {
    try {
        const response = await fetch(`${getApiUrl()}/api/records`);
        const data = await response.json();
        if (data.success) {
            document.getElementById('dashboardRecords').textContent = data.total_records;
        }
    } catch (error) {
        console.error('Load records error:', error);
    }
}

// REGISTER DATA

function addSensorReading() {
    const sensorReadings = document.getElementById('sensorReadings');
    if (!sensorReadings) return;
    const readingId = 'sensor-' + Date.now();
    const sensorOptions = [
        { value: 'temperature', label: 'Temperature', unit: '°C' },
        { value: 'humidity', label: 'Humidity', unit: '%' },
        { value: 'pressure', label: 'Pressure', unit: 'hPa' },
        { value: 'motion', label: 'Motion', unit: 'T/F' },
        { value: 'gps', label: 'GPS', unit: 'coordinates' },
        { value: 'co2', label: 'CO2', unit: 'ppm' },
        { value: 'dust', label: 'Dust', unit: 'µg/m³' }
    ];
    const optionsHtml = sensorOptions.map(s => `<option value="${s.value}">${s.label}</option>`).join('');
    const readingHtml = `
        <div class="card mb-3 border-primary sensor-reading-card" id="${readingId}">
            <div class="card-body pb-2">
                <div class="row">
                    <div class="col-md-5">
                        <label class="form-label small">Sensor Type</label>
                        <select class="form-select form-select-sm sensor-type-select" onchange="updateSensorInputType(this, '${readingId}')">
                            <option value="">Select sensor...</option>
                            ${optionsHtml}
                        </select>
                    </div>
                    <div class="col-md-5">
                        <label class="form-label small">Value</label>
                        <div class="input-group input-group-sm">
                            <input type="text" class="form-control sensor-value" placeholder="e.g., 25.5" required>
                            <span class="input-group-text sensor-unit">-</span>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label small">&nbsp;</label>
                        <button type="button" class="btn btn-sm btn-danger w-100" onclick="removeSensorReading('${readingId}')">
                            <i class="bi bi-trash"></i> Remove
                        </button>
                    </div>
                </div>
            </div>
        </div>`;
    const readingDiv = document.createElement('div');
    readingDiv.innerHTML = readingHtml;
    sensorReadings.appendChild(readingDiv.firstElementChild);
}

function updateSensorInputType(selectElement, readingId) {
    const sensorType = selectElement.value;
    const card = document.getElementById(readingId);
    const input = card.querySelector('.sensor-value');
    const unitSpan = card.querySelector('.sensor-unit');
    const units = {
        'temperature': '°C', 'humidity': '%', 'pressure': 'hPa',
        'motion': 'true/false', 'gps': 'lat,lon', 'co2': 'ppm', 'dust': 'µg/m³'
    };
    unitSpan.textContent = units[sensorType] || '-';
    if (sensorType === 'motion') {
        input.setAttribute('type', 'text');
        input.placeholder = 'true or false';
    } else if (sensorType === 'gps') {
        input.setAttribute('type', 'text');
        input.placeholder = 'e.g., 40.7128,-74.0060';
    } else {
        input.setAttribute('type', 'number');
        input.step = '0.01';
        input.placeholder = 'e.g., 25.5';
    }
}

function removeSensorReading(readingId) {
    const element = document.getElementById(readingId);
    if (element) element.remove();
}

async function handleRegister(e) {
    e.preventDefault();
    const deviceId = document.getElementById('deviceId')?.value.trim();
    if (!deviceId) { showAlert('Please enter a Device ID', 'warning'); return; }

    let sensorData = {};
    document.querySelectorAll('.sensor-reading-card').forEach((card) => {
        const typeSelect = card.querySelector('.sensor-type-select');
        const valueInput = card.querySelector('.sensor-value');
        if (typeSelect && valueInput) {
            const sensorType = typeSelect.value;
            const value = valueInput.value?.trim();
            if (sensorType && value) {
                if (sensorType === 'motion') {
                    sensorData[sensorType] = value.toLowerCase();
                } else {
                    sensorData[sensorType] = isNaN(value) ? value : parseFloat(value);
                }
            }
        }
    });

    document.querySelectorAll('.field-wrapper').forEach(wrapper => {
        const name = wrapper.querySelector('.field-name')?.value.trim();
        const value = wrapper.querySelector('.field-value')?.value.trim();
        if (name && value) sensorData[name] = isNaN(value) ? value : parseFloat(value);
    });

    if (Object.keys(sensorData).length === 0) { showAlert('Please add at least one sensor reading', 'warning'); return; }

    const hash = await computeHash(sensorData);
    const hashInput = document.getElementById('generatedHash');
    if (hashInput) hashInput.value = hash;

    try {
        const response = await fetch(`${getApiUrl()}/api/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device_id: deviceId, sensor_data: sensorData })
        });
        const data = await response.json();
        const resultDiv = document.getElementById('registerResult');
        if (data.success) {
            showAlert('Data registered successfully!', 'success');
            resultDiv.innerHTML = `
                <div class="result-box success">
                    <h6 class="text-success mb-3"><i class="bi bi-check-circle"></i> Registration Successful</h6>
                    <table class="table table-sm table-borderless">
                        <tr><td><strong>Device ID:</strong></td><td>${data.device_id}</td></tr>
                        <tr><td><strong>Sensors:</strong></td><td>${Object.keys(sensorData).join(', ')}</td></tr>
                        <tr><td><strong>Data Hash:</strong></td><td><code class="small">${data.data_hash}</code></td></tr>
                        <tr><td><strong>TX Hash:</strong></td><td><code class="small">${data.tx_hash}</code></td></tr>
                        <tr><td><strong>Block Number:</strong></td><td>${data.block_number}</td></tr>
                        <tr><td><strong>Gas Used:</strong></td><td>${data.gas_used}</td></tr>
                        <tr><td><strong>Timestamp:</strong></td><td>${new Date(data.timestamp).toLocaleString()}</td></tr>
                    </table>
                    <button class="btn btn-sm btn-primary" onclick="copyToClipboard('${data.data_hash}')">
                        <i class="bi bi-clipboard"></i> Copy Hash
                    </button>
                </div>`;
            document.getElementById('registerForm').reset();
            document.getElementById('sensorReadings').innerHTML = '';
            document.getElementById('customFields').innerHTML = '';
            setTimeout(() => addSensorReading(), 100);
            setTimeout(() => { loadHealth(); loadStatistics(); loadAuditReport(); }, 1500);
        } else {
            showAlert('Registration failed', 'danger');
            resultDiv.innerHTML = `<div class="result-box error"><h6 class="text-danger"><i class="bi bi-exclamation-circle"></i> Failed</h6><p>${data.error || 'Unknown error'}</p></div>`;
        }
    } catch (error) {
        showAlert('Connection error: ' + error.message, 'danger');
        document.getElementById('registerResult').innerHTML = `<div class="result-box error"><p>${error.message}</p></div>`;
    }
}

// VERIFY DATA

async function computeVerifyHash() {
    try {
        const jsonInput = document.getElementById('verifyJsonInput').value;
        const data = JSON.parse(jsonInput);
        const hash = await computeHash(data);
        document.getElementById('verifyHash').value = hash;
        showAlert('Hash computed successfully!', 'info');
    } catch (error) {
        showAlert('Invalid JSON input: ' + error.message, 'danger');
    }
}

async function handleVerify(e) {
    e.preventDefault();
    try {
        const sensorData = JSON.parse(document.getElementById('verifyJsonInput').value);
        const response = await fetch(`${getApiUrl()}/api/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sensor_data: sensorData })
        });
        const data = await response.json();
        const resultDiv = document.getElementById('verifyResult');
        if (data.integrity_verified) {
            resultDiv.innerHTML = `
                <div class="result-box success">
                    <h6 class="text-success mb-3"><i class="bi bi-check-circle"></i> Data Integrity Verified</h6>
                    <table class="table table-sm table-borderless">
                        <tr><td><strong>Status:</strong></td><td><span class="badge bg-success">Verified</span></td></tr>
                        <tr><td><strong>Hash:</strong></td><td><code class="small">${data.computed_hash}</code></td></tr>
                        <tr><td><strong>Message:</strong></td><td>${data.message}</td></tr>
                        <tr><td><strong>Timestamp:</strong></td><td>${new Date(data.timestamp).toLocaleString()}</td></tr>
                    </table>
                </div>`;
            showAlert('Data integrity confirmed!', 'success');
        } else {
            resultDiv.innerHTML = `<div class="result-box error"><h6 class="text-danger"><i class="bi bi-exclamation-circle"></i> Verification Failed</h6><p>${data.message}</p></div>`;
            showAlert('Integrity could not be verified!', 'danger');
        }
    } catch (error) {
        document.getElementById('verifyResult').innerHTML = `<div class="result-box error"><p>${error.message}</p></div>`;
    }
}

async function handleVerifyDevice(e) {
    e.preventDefault();
    const deviceId = document.getElementById('deviceIdVerify').value;
    const resultDiv = document.getElementById('verifyDeviceResult');
    if (!deviceId.trim()) { showAlert('Please enter a device ID', 'warning'); return; }
    resultDiv.innerHTML = `<div class="text-center"><div class="spinner-border spinner-small"></div> Searching blockchain...</div>`;
    try {
        const response = await fetch(`${getApiUrl()}/api/search-device`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device_id: deviceId })
        });
        const data = await response.json();
        if (data.success && data.records.length > 0) {
            let rows = data.records.map(r => `
                <tr>
                    <td><code class="small">${r.data_hash.substring(0, 16)}...</code></td>
                    <td><code class="small">${r.device_address.substring(0, 10)}...</code></td>
                    <td>${new Date(r.timestamp * 1000).toLocaleString()}</td>
                </tr>`).join('');
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="bi bi-check-circle"></i> Device Found: ${deviceId} — ${data.count} record(s)</h6>
                    <table class="table table-sm table-hover">
                        <thead><tr><th>Data Hash</th><th>Device Address</th><th>Timestamp</th></tr></thead>
                        <tbody>${rows}</tbody>
                    </table>
                </div>`;
        } else {
            resultDiv.innerHTML = `<div class="alert alert-warning"><h6><i class="bi bi-exclamation-circle"></i> Device Not Found</h6><p>No records for: <strong>${deviceId}</strong></p></div>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<div class="alert alert-danger"><p>Error: ${error.message}</p></div>`;
    }
}

// HASH GENERATOR

async function handleHash(e) {
    e.preventDefault();
    try {
        const inputData = JSON.parse(document.getElementById('hashInput').value);
        const response = await fetch(`${getApiUrl()}/api/hash`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: inputData })
        });
        const data = await response.json();
        const resultDiv = document.getElementById('hashResult');
        if (data.success) {
            resultDiv.innerHTML = `
                <div class="result-box success">
                    <h6 class="text-success mb-3"><i class="bi bi-key"></i> Hash Generated Successfully</h6>
                    <label class="form-label">SHA-256 Hash:</label>
                    <div class="hash-display mb-3">${data.hash}</div>
                    <table class="table table-sm table-borderless">
                        <tr><td><strong>Algorithm:</strong></td><td>${data.algorithm}</td></tr>
                        <tr><td><strong>Hash Length:</strong></td><td>${data.hash_length} characters</td></tr>
                        <tr><td><strong>Timestamp:</strong></td><td>${new Date(data.timestamp).toLocaleString()}</td></tr>
                    </table>
                    <button class="btn btn-sm btn-primary" onclick="copyToClipboard('${data.hash}')">
                        <i class="bi bi-clipboard"></i> Copy Hash
                    </button>
                </div>`;
            showAlert('Hash generated successfully!', 'success');
        } else {
            resultDiv.innerHTML = `<div class="result-box error"><p>${data.error}</p></div>`;
        }
    } catch (error) {
        document.getElementById('hashResult').innerHTML = `<div class="result-box error"><p>${error.message}</p></div>`;
    }
}

// AUDIT

async function loadAuditReport() {
    const auditContent = document.getElementById('auditContent');
    auditContent.innerHTML = '<div class="text-center p-4"><div class="spinner-border" role="status"></div></div>';
    try {
        const response = await fetch(`${getApiUrl()}/api/audit`);
        const data = await response.json();
        if (data.success) {
            const report = data.audit_report;
            auditContent.innerHTML = `
                <div class="mb-4">
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <div class="card bg-success text-white">
                                <div class="card-body">
                                    <h6 class="card-title">Total Successful Registrations</h6>
                                    <h3>${report.total_successful_registrations}</h3>
                                    <small>${report.overall_success_rate} Success Rate</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card bg-secondary text-white">
                                <div class="card-body">
                                    <h6 class="card-title">Status</h6>
                                    <p class="mb-0"><small>API Server Instance</small></p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-body">
                            <h6 class="mb-2">System Details</h6>
                            <table class="table table-sm mb-0">
                                <tbody>
                                    <tr><td><strong>System Status:</strong></td><td><span class="badge bg-success">${report.system_status}</span></td></tr>
                                    <tr><td><strong>Blockchain Network:</strong></td><td><code>${report.blockchain_network}</code></td></tr>
                                    <tr><td><strong>Contract Address:</strong></td><td><code>${report.contract_address}</code></td></tr>
                                    <tr><td><strong>Report Time:</strong></td><td>${new Date(report.report_timestamp).toLocaleString()}</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>`;
        } else {
            auditContent.innerHTML = `<div class="alert alert-danger">Failed: ${data.error}</div>`;
        }
    } catch (error) {
        auditContent.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

// STATISTICS

async function loadStatistics() {
    try {
        const response = await fetch(`${getApiUrl()}/api/stats`);
        const data = await response.json();
        if (data.success) {
            const stats = data.statistics;
            document.getElementById('statsTotalRecords').textContent = stats.total_blockchain_records || '0';
            document.getElementById('statsProcessedRecords').textContent = stats.total_processed_records || '0';
            document.getElementById('statsBalance').textContent = stats.account_balance || '--';
            document.getElementById('statsDetail').innerHTML = `
                <table class="table">
                    <tbody>
                        <tr><td><strong>Blockchain Records:</strong></td><td><strong class="text-primary">${stats.total_blockchain_records || 0}</strong></td></tr>
                        <tr><td><strong>Processed Records:</strong></td><td><strong class="text-success">${stats.total_processed_records || 0}</strong></td></tr>
                        <tr><td><strong>Account Balance:</strong></td><td>${stats.account_balance || '--'}</td></tr>
                        <tr><td><strong>Contract Address:</strong></td><td><code class="small">${stats.contract_address}</code></td></tr>
                        <tr><td><strong>Network URL:</strong></td><td><code class="small">${stats.network_url}</code></td></tr>
                        <tr><td><strong>System Status:</strong></td><td><span class="badge bg-success">${stats.system_uptime}</span></td></tr>
                    </tbody>
                </table>`;
        }
    } catch (error) {
        console.error('Statistics load error:', error);
    }
}

// HELPERS

async function computeHash(data) {
    try {
        const response = await fetch(`${getApiUrl()}/api/hash`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: data })
        });
        const result = await response.json();
        if (result.success) return result.hash;
    } catch (error) {
        console.error('Hash computation error:', error);
    }
    return '';
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Copied to clipboard!', 'success');
    }).catch(err => {
        showAlert('Failed to copy: ' + err.message, 'danger');
    });
}

function addCustomField() {
    const customFields = document.getElementById('customFields');
    const fieldId = 'custom-' + Date.now();
    const fieldDiv = document.createElement('div');
    fieldDiv.id = fieldId;
    fieldDiv.innerHTML = `
        <div class="field-wrapper">
            <div class="row mb-3">
                <div class="col-md-5"><input type="text" class="form-control field-name" placeholder="Field name"></div>
                <div class="col-md-5"><input type="text" class="form-control field-value" placeholder="Field value"></div>
                <div class="col-md-2"><button type="button" class="btn btn-sm btn-danger w-100" onclick="removeCustomField('${fieldId}')"><i class="bi bi-trash"></i></button></div>
            </div>
        </div>`;
    customFields.appendChild(fieldDiv);
}

function removeCustomField(fieldId) {
    document.getElementById(fieldId)?.remove();
}

function setupAutoRefresh() {
    if (config.autoRefresh) {
        setInterval(() => {
            const activeTab = document.querySelector('.nav-link.active');
            if (activeTab?.id === 'dashboard-tab') loadHealth();
        }, config.refreshInterval);
    }
}
