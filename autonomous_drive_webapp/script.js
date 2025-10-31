const ws = new WebSocket("ws://192.168.1.66:8080");

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  document.getElementById("LCount").textContent = data.LCount;
  document.getElementById("LW").textContent = data.LW.toFixed(2);
  document.getElementById("RCount").textContent = data.RCount;
  document.getElementById("RW").textContent = data.RW.toFixed(2);
};

ws.onopen = () => console.log("✅ WebSocket connected");
ws.onerror = (e) => console.error("❌ WebSocket error", e);
