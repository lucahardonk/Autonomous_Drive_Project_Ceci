const ws = new WebSocket("ws://192.168.1.66:8080");

ws.onmessage = (event) => {
  console.log("📥 UI received:", event.data);  
  const data = JSON.parse(event.data);

  document.getElementById("LCount").textContent = data.LCount;
  document.getElementById("L_RPM").textContent = data.L_RPM.toFixed(2);
  document.getElementById("RCount").textContent = data.RCount;
  document.getElementById("R_RPM").textContent = data.R_RPM.toFixed(2);
};


ws.onopen = () => console.log("✅ WebSocket connected");
ws.onerror = (e) => console.error("❌ WebSocket error", e);
