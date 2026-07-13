"""
dashboard.py - Professional Dark Theme Web Dashboard with Charts
Run: python3 dashboard.py
Browser: http://localhost:5000
"""

import json, os
from datetime import datetime
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)
ALERTS_PATH = os.path.join("data", "alerts.json")

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Network IDS</title>
<meta http-equiv="refresh" content="5">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0d1117;color:#c9d1d9;font-family:'Courier New',monospace;font-size:13px}

header{
  background:#161b22;border-bottom:1px solid #21262d;
  padding:12px 24px;display:flex;align-items:center;gap:10px
}
header h1{font-size:15px;font-weight:500;color:#e6edf3}
.live-dot{width:8px;height:8px;background:#3fb950;border-radius:50%;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.2}}
.badge{background:#1f6feb22;color:#58a6ff;font-size:10px;padding:2px 8px;border-radius:10px;border:1px solid #1f6feb44}
.ts{font-size:11px;color:#8b949e;margin-left:auto}

.body{padding:16px 24px}

.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}
.stat{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px}
.stat-lbl{font-size:10px;color:#8b949e;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px}
.stat-val{font-size:28px;font-weight:500;line-height:1}
.stat-sub{font-size:10px;color:#8b949e;margin-top:4px}
.cr{color:#f85149}.co{color:#e3b341}.cb{color:#58a6ff}.cg{color:#3fb950}.cp{color:#a371f7}

.chart-grid{display:grid;grid-template-columns:1fr 2fr;gap:10px;margin-bottom:14px}
.panel{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px}
.ptitle{font-size:10px;color:#8b949e;text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px}

table{width:100%;border-collapse:collapse}
th{color:#8b949e;font-weight:400;text-align:left;padding:6px 8px;border-bottom:1px solid #21262d;font-size:10px;text-transform:uppercase;letter-spacing:.4px}
td{padding:7px 8px;border-bottom:1px solid #161b22;vertical-align:middle}
tr:last-child td{border-bottom:none}
tr:hover td{background:#1c2128}

.tag{display:inline-block;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:500}
.PORT_SCAN  {background:#a371f722;color:#a371f7;border:1px solid #a371f744}
.DDOS_FLOOD {background:#f8514922;color:#f85149;border:1px solid #f8514944}
.BRUTE_FORCE{background:#e3b34122;color:#e3b341;border:1px solid #e3b34144}
.ANOMALY    {background:#58a6ff22;color:#58a6ff;border:1px solid #58a6ff44}

.sev-HIGH  {color:#f85149;font-size:10px;font-weight:500}
.sev-MEDIUM{color:#e3b341;font-size:10px;font-weight:500}
.sev-LOW   {color:#3fb950;font-size:10px;font-weight:500}

.conf-bar{display:flex;align-items:center;gap:5px}
.conf-track{width:44px;height:4px;background:#21262d;border-radius:2px;overflow:hidden}
.conf-fill{height:100%;border-radius:2px;background:#f85149}

.footer{display:flex;gap:12px;align-items:center;padding-top:10px;border-top:1px solid #21262d;margin-top:4px}
.footer span{font-size:10px;color:#8b949e}
.dot{width:6px;height:6px;border-radius:50%;display:inline-block;margin-right:3px}
.mono{font-family:'Courier New',monospace;font-size:10px}
.empty{text-align:center;color:#3fb950;padding:24px;font-size:12px}
</style>
</head>
<body>

<header>
  <div class="live-dot"></div>
  <h1>Network IDS Dashboard</h1>
  <span class="badge">LIVE</span>
  <span class="ts">{{ now }}</span>
</header>

<div class="body">

  <!-- Stat cards -->
  <div class="stat-grid">
    <div class="stat">
      <div class="stat-lbl">Total alerts</div>
      <div class="stat-val cr">{{ stats.total }}</div>
      <div class="stat-sub">all time</div>
    </div>
    <div class="stat">
      <div class="stat-lbl">Port scans</div>
      <div class="stat-val cp">{{ stats.port_scan }}</div>
      <div class="stat-sub">nmap / masscan</div>
    </div>
    <div class="stat">
      <div class="stat-lbl">DDoS floods</div>
      <div class="stat-val cr">{{ stats.ddos }}</div>
      <div class="stat-sub">packet rate spike</div>
    </div>
    <div class="stat">
      <div class="stat-lbl">Brute force</div>
      <div class="stat-val co">{{ stats.brute }}</div>
      <div class="stat-sub">SSH / FTP / RDP</div>
    </div>
  </div>

  <!-- Charts row -->
  <div class="chart-grid">

    <!-- Doughnut -->
    <div class="panel">
      <div class="ptitle">Attack breakdown</div>
      <canvas id="donut" height="200"></canvas>
    </div>

    <!-- Timeline -->
    <div class="panel">
      <div class="ptitle">Alert timeline (last 30 alerts)</div>
      <canvas id="timeline" height="200"></canvas>
    </div>

  </div>

  <!-- Alerts table -->
  <div class="panel" style="margin-bottom:14px">
    <div class="ptitle">Recent alerts (last 50)</div>
    {% if alerts %}
    <table>
      <tr>
        <th>Time</th><th>Type</th><th>Severity</th>
        <th>Source</th><th>Destination</th><th>Confidence</th><th>Reason</th>
      </tr>
      {% for a in alerts %}
      <tr>
        <td class="mono" style="color:#8b949e">{{ a.timestamp[11:19] }}</td>
        <td><span class="tag {{ a.attack_type }}">{{ a.attack_type.replace('_',' ') }}</span></td>
        <td><span class="sev-{{ a.severity }}">{{ a.severity }}</span></td>
        <td class="mono">{{ a.src_ip }}:{{ a.src_port }}</td>
        <td class="mono">{{ a.dst_ip }}:{{ a.dst_port }}</td>
        <td>
          <div class="conf-bar">
            <div class="conf-track">
              <div class="conf-fill" style="width:{{ (a.confidence*100)|int }}%"></div>
            </div>
            <span style="font-size:10px;color:#8b949e">{{ "%.0f"|format(a.confidence*100) }}%</span>
          </div>
        </td>
        <td style="color:#8b949e;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
          {{ a.reason[:50] }}
        </td>
      </tr>
      {% endfor %}
    </table>
    {% else %}
    <div class="empty">No alerts detected — network is clean</div>
    {% endif %}
  </div>

  <div class="footer">
    <span><span class="dot" style="background:#a371f7"></span>Port scan</span>
    <span><span class="dot" style="background:#f85149"></span>DDoS flood</span>
    <span><span class="dot" style="background:#e3b341"></span>Brute force</span>
    <span><span class="dot" style="background:#58a6ff"></span>Anomaly</span>
    <span style="margin-left:auto">Auto-refresh: 5s</span>
  </div>

</div>

<script>
// ── Doughnut chart ──────────────────────────────────────────────
const donutCtx = document.getElementById('donut').getContext('2d');
new Chart(donutCtx, {
  type: 'doughnut',
  data: {
    labels: ['Port Scan', 'DDoS Flood', 'Brute Force', 'Anomaly'],
    datasets: [{
      data: [
        {{ stats.port_scan }},
        {{ stats.ddos }},
        {{ stats.brute }},
        {{ stats.anomaly }}
      ],
      backgroundColor: ['#a371f7', '#f85149', '#e3b341', '#58a6ff'],
      borderColor:     ['#a371f744','#f8514944','#e3b34144','#58a6ff44'],
      borderWidth: 1,
      hoverOffset: 6,
    }]
  },
  options: {
    responsive: true,
    cutout: '65%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#8b949e',
          font: { size: 11, family: 'Courier New' },
          boxWidth: 10,
          padding: 12,
        }
      }
    }
  }
});

// ── Timeline line chart ─────────────────────────────────────────
// Group last 30 alerts by minute bucket
const raw = {{ timeline | tojson }};
const labels  = raw.map(r => r.t);
const counts  = raw.map(r => r.c);

const tlCtx = document.getElementById('timeline').getContext('2d');
new Chart(tlCtx, {
  type: 'line',
  data: {
    labels: labels,
    datasets: [{
      label: 'Alerts',
      data: counts,
      borderColor: '#f85149',
      backgroundColor: 'rgba(248,81,73,0.1)',
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#f85149',
      pointRadius: 4,
      pointHoverRadius: 6,
    }]
  },
  options: {
    responsive: true,
    scales: {
      x: {
        ticks: { color:'#8b949e', font:{size:10,family:'Courier New'} },
        grid:  { color:'#21262d' }
      },
      y: {
        beginAtZero: true,
        ticks: { color:'#8b949e', font:{size:10,family:'Courier New'}, precision:0 },
        grid:  { color:'#21262d' }
      }
    },
    plugins: {
      legend: { labels:{ color:'#8b949e', font:{size:11,family:'Courier New'} } }
    }
  }
});
</script>

</body>
</html>
"""


def load_alerts():
    if not os.path.exists(ALERTS_PATH):
        return []
    alerts = []
    with open(ALERTS_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    alerts.append(json.loads(line))
                except:
                    pass
    return alerts


def build_timeline(alerts, n=30):
    """Group last n alerts into 1-minute buckets for the line chart."""
    recent = alerts[-n:]
    buckets = {}
    for a in recent:
        t = a["timestamp"][11:16]  # HH:MM
        buckets[t] = buckets.get(t, 0) + 1
    return [{"t": k, "c": v} for k, v in sorted(buckets.items())]


@app.route("/")
def index():
    alerts = load_alerts()
    stats = {
        "total":     len(alerts),
        "port_scan": sum(1 for a in alerts if a.get("attack_type") == "PORT_SCAN"),
        "ddos":      sum(1 for a in alerts if a.get("attack_type") == "DDOS_FLOOD"),
        "brute":     sum(1 for a in alerts if a.get("attack_type") == "BRUTE_FORCE"),
        "anomaly":   sum(1 for a in alerts if a.get("attack_type") == "ANOMALY"),
    }
    return render_template_string(
        HTML,
        alerts=list(reversed(alerts[-50:])),
        stats=stats,
        timeline=build_timeline(alerts),
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.route("/api/stats")
def api_stats():
    alerts = load_alerts()
    return jsonify({
        "total":     len(alerts),
        "port_scan": sum(1 for a in alerts if a.get("attack_type") == "PORT_SCAN"),
        "ddos":      sum(1 for a in alerts if a.get("attack_type") == "DDOS_FLOOD"),
        "brute":     sum(1 for a in alerts if a.get("attack_type") == "BRUTE_FORCE"),
        "anomaly":   sum(1 for a in alerts if a.get("attack_type") == "ANOMALY"),
    })


if __name__ == "__main__":
    print("[dashboard] http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
