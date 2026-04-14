const API = "https://ai-firewall-2df6.onrender.com";

let chartInstance = null;

async function sendRequest() {
    try {
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

        loadLogs(); // refresh dashboard after request
    } catch (err) {
        console.error(err);
        document.getElementById("result").innerText = "Error connecting to API";
    }
}

async function loadLogs() {
    try {
        let res = await fetch(API + "/logs");
        let data = await res.json();

        if (!data || data.length === 0) {
            console.log("No data");
            return;
        }

        let attacks = data.filter(d => d.attack !== "Normal").length;
        let normal = data.filter(d => d.attack === "Normal").length;

        document.getElementById("attacks").innerText = attacks;
        document.getElementById("normal").innerText = normal;

        // Chart Data
        let counts = {};
        data.forEach(d => {
            counts[d.attack] = (counts[d.attack] || 0) + 1;
        });

        let ctx = document.getElementById("attackChart");

        if (chartInstance) chartInstance.destroy();

        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(counts),
                datasets: [{
                    label: 'Attack Types',
                    data: Object.values(counts)
                }]
            }
        });

        // Logs Table
        let table = "<tr><th>IP</th><th>Attack</th></tr>";
        data.slice(0, 20).forEach(d => {
            table += `<tr><td>${d.ip}</td><td>${d.attack}</td></tr>`;
        });

        document.getElementById("logsTable").innerHTML = table;

        // Map
        let mapContainer = document.getElementById("map");
        mapContainer.innerHTML = "";

        let map = L.map('map').setView([20, 78], 3);

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

        data.forEach(d => {
            if (d.lat && d.lon) {
                L.marker([d.lat, d.lon]).addTo(map);
            }
        });

    } catch (err) {
        console.error("Logs error:", err);
    }
}

// Run after page loads
window.onload = loadLogs;