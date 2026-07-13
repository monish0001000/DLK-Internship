// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // 1. Live Clock
    const clockEl = document.getElementById('liveClock');
    if (clockEl) {
        setInterval(() => {
            const now = new Date();
            clockEl.textContent = now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
        }, 1000);
    }

    // 2. Auto-dismiss Flash Messages
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 300);
        }, 5000);
        flash.addEventListener('click', () => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 300);
        });
    });

    // 3. Initialize Dashboard Charts (if present)
    initCharts();

    // 4. Threat Hunting Editor Logic
    initHuntingEditor();
});

function initCharts() {
    // Colors mapped from CSS variables
    const colors = {
        critical: '#ef4444',
        high: '#f97316',
        medium: '#f59e0b',
        low: '#10b981',
        info: '#6366f1',
        blue: '#00d4ff',
        purple: '#7c3aed',
        text: '#94a3b8',
        grid: 'rgba(255,255,255,0.05)'
    };

    // Risk Donut Chart
    const riskCtx = document.getElementById('riskChart');
    if (riskCtx) {
        const riskData = JSON.parse(riskCtx.dataset.risks || '{}');
        new Chart(riskCtx, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
                datasets: [{
                    data: [
                        riskData.critical || 0,
                        riskData.high || 0,
                        riskData.medium || 0,
                        riskData.low || 0,
                        riskData.info || 0
                    ],
                    backgroundColor: [
                        colors.critical, colors.high, colors.medium, colors.low, colors.info
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                cutout: '75%',
                plugins: {
                    legend: { position: 'right', labels: { color: colors.text, font: {family: 'Inter'} } }
                }
            }
        });
    }

    // Event Trends Line Chart
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx) {
        const labels = JSON.parse(trendCtx.dataset.labels || '[]');
        const data = JSON.parse(trendCtx.dataset.counts || '[]');
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Events',
                    data: data,
                    borderColor: colors.blue,
                    backgroundColor: 'rgba(0,212,255,0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: colors.purple,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 1,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { grid: { color: colors.grid }, ticks: { color: colors.text } },
                    x: { grid: { color: colors.grid }, ticks: { color: colors.text } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}

function initHuntingEditor() {
    const runBtn = document.getElementById('runQueryBtn');
    const queryInput = document.getElementById('queryInput');
    const resultsDiv = document.getElementById('queryResults');
    const presetChips = document.querySelectorAll('.preset-chip');

    if (!runBtn || !queryInput) return;

    // Handle Presets
    presetChips.forEach(chip => {
        chip.addEventListener('click', () => {
            queryInput.value = chip.dataset.query;
        });
    });

    // Run Query
    runBtn.addEventListener('click', async () => {
        const query = queryInput.value.trim();
        if (!query) return;

        runBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Running...';
        runBtn.disabled = true;
        resultsDiv.innerHTML = '<div class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><p>Executing osquery...</p></div>';

        try {
            const res = await fetch('/hunting/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            const data = await res.json();

            if (data.error) {
                resultsDiv.innerHTML = `<div class="flash flash-danger" style="position:relative;top:0;right:0;max-width:none;"><i class="fa-solid fa-triangle-exclamation"></i> Error: ${data.error}</div>`;
            } else if (data.results && data.results.length > 0) {
                renderTable(data.results, resultsDiv);
            } else {
                resultsDiv.innerHTML = '<div class="empty-state"><i class="fa-solid fa-check"></i><p>Query successful. 0 rows returned.</p></div>';
            }
        } catch (err) {
            resultsDiv.innerHTML = `<div class="flash flash-danger" style="position:relative;top:0;right:0;max-width:none;"><i class="fa-solid fa-triangle-exclamation"></i> Network Error</div>`;
        } finally {
            runBtn.innerHTML = '<i class="fa-solid fa-play"></i> Run Query';
            runBtn.disabled = false;
        }
    });
}

function renderTable(data, container) {
    if (!data.length) return;
    const columns = Object.keys(data[0]);
    
    let html = '<div class="table-wrapper"><table class="data-table"><thead><tr>';
    columns.forEach(col => html += `<th>${col}</th>`);
    html += '</tr></thead><tbody>';
    
    data.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            const val = row[col] !== null && row[col] !== undefined ? row[col] : '';
            html += `<td>${String(val).substring(0, 100)}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    html += `<p class="text-muted mt-2" style="font-size:12px;">Total rows: ${data.length}</p>`;
    container.innerHTML = html;
}

// 5. WebSockets for Real-time Alerts
if (typeof io !== 'undefined') {
    const socket = io();
    socket.on('new_alert', function(data) {
        const container = document.querySelector('.flash-container');
        if(container) {
            const html = `<div class="flash flash-${data.severity}" style="cursor:pointer; box-shadow: 0 0 15px var(--sev-${data.severity});" onclick="window.location.href='/alerts'">
                <i class="fa-solid fa-triangle-exclamation"></i>
                <strong>[${data.name}]</strong> on ${data.hostname}: ${data.desc}
            </div>`;
            container.insertAdjacentHTML('beforeend', html);
        }
    });
}

// 6. Kill Process Action
document.body.addEventListener('click', async (e) => {
    const btn = e.target.closest('.btn-kill');
    if(btn) {
        const pid = btn.dataset.pid;
        if(!pid || pid === '-') return;
        
        if(!confirm(`⚠️ ACTIVE RESPONSE\n\nAre you sure you want to forcefully terminate Process ID ${pid}?`)) return;
        
        const originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
        
        try {
            const res = await fetch(`/api/kill/${pid}`, { method: 'POST' });
            const data = await res.json();
            alert(data.message);
            if(data.status === 'success') {
                btn.style.backgroundColor = 'var(--sev-low)';
                btn.innerHTML = '<i class="fa-solid fa-check"></i> Killed';
            } else {
                btn.innerHTML = originalHtml;
                btn.disabled = false;
            }
        } catch(err) {
            alert('Error killing process.');
            btn.innerHTML = originalHtml;
            btn.disabled = false;
        }
    }
});
