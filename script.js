const API = "https://ai-firewall-2df6.onrender.com";

let charts = {};

async function sendRequest() {
    let req = document.getElementById("req").value || 100;
    let fail = document.getElementById("fail").value || 5;
    let url = document.getElementById("url").value || "home";

    let res = await fetch(API + "/predict", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            requests: parseInt(req),
            failed_logins: parseInt(fail),
            url: url
        })
    });

    let data = await res.json();

    document.getElementById("result").innerText = JSON.stringify(data, null, 2);

    // SHAP
    if (data.shap) {
        renderChart("shapChart", Object.keys(data.shap), Object.values(data.shap));
    }

    loadLogs();
}

async function loadLogs() {
    let res = await fetch(API + "/logs");
    let data = await res.json();

    if (!data.length) return;

    // Metrics
    let attacks = data.filter(d => d.attack !== "Normal").length;
    let normal = data.filter(d => d.attack === "Normal").length;

    document.getElementById("attacks").innerText = attacks;
    document.getElementById("normal").innerText = normal;

    // Retrain
    let r = await fetch(API + "/retrain_count");
    let rdata = await r.json();
    document.getElementById("retrain").innerText = rdata.retrain_count;

    // Attack Types
    let attackCounts = countBy(data, "attack");
    renderChart("attackChart", Object.keys(attackCounts), Object.values(attackCounts));

    // Requests Trend
    let requests = data.map(d => d.requests);
    renderChart("trendChart", requests.map((_, i) => i), requests, "line");

    // IP Chart
    let ipCounts = countBy(data, "ip");
    renderChart("ipChart", Object.keys(ipCounts), Object.values(ipCounts));

    // Reason Chart
    let reasons = {};
    data.forEach(d => {
        (d.reason || "").split(", ").forEach(r => {
            if (r) reasons[r] = (reasons[r] || 0) + 1;
        });
    });
    renderChart("reasonChart", Object.keys(reasons), Object.values(reasons));

    // Logs Table FULL
    let table = "<tr><th>IP</th><th>Requests</th><th>Failed</th><th>Attack</th><th>Reason</th><th>Time</th></tr>";
    data.slice(0, 20).forEach(d => {
        table += `<tr>
            <td>${d.ip}</td>
            <td>${d.requests}</td>
            <td>${d.failed_logins}</td>
            <td>${d.attack}</td>
            <td>${d.reason}</td>
            <td>${d.timestamp}</td>
        </tr>`;
    });
    document.getElementById("logsTable").innerHTML = table;

    // Map
    document.getElementById("map").innerHTML = "";
    let map = L.map('map').setView([20, 78], 3);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    data.forEach(d => {
        if (d.lat && d.lon) {
            L.marker([d.lat, d.lon]).addTo(map);
        }
    });
}

function countBy(data, key) {
    let result = {};
    data.forEach(d => {
        result[d[key]] = (result[d[key]] || 0) + 1;
    });
    return result;
}

function renderChart(id, labels, values, type="bar") {
    if (charts[id]) charts[id].destroy();

    charts[id] = new Chart(document.getElementById(id), {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: id,
                data: values
            }]
        }
    });
}

window.onload = loadLogs;
