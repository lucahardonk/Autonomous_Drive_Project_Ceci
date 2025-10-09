const baseURL = "http://192.168.1.162"; // Replace with your Arduino IP
let direction = "forward";
let steerAngle = 0;
let minLeft = -70, maxRight = 70, center = 0;

// Fetch sterzo limits
fetch(baseURL + "/steer/limits")
  .then(r => r.json())
  .then(data => {
    minLeft = data.minLeft - data.center;
    maxRight = data.maxRight - data.center;
    center = data.center;
    console.log("✅ Sterzo limits:", minLeft, maxRight, center);
  });

// Canvas steering wheel
const canvas = document.getElementById("wheel");
const ctx = canvas.getContext("2d");
const radius = canvas.width / 2;
let isSteering = false;
let lastAngle = 0;

// Draw wheel
function drawWheel(angle = 0) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.save();
  ctx.translate(radius, radius);
  ctx.rotate((angle * Math.PI) / 180);
  ctx.beginPath();
  ctx.arc(0, 0, radius - 10, 0, 2 * Math.PI);
  ctx.strokeStyle = "#888";
  ctx.lineWidth = 10;
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(0, -radius + 30);
  ctx.lineTo(0, radius - 30);
  ctx.strokeStyle = "#fff";
  ctx.lineWidth = 4;
  ctx.stroke();
  ctx.restore();
}
drawWheel();

// Steering interaction
canvas.addEventListener("mousedown", startSteer);
canvas.addEventListener("touchstart", startSteer);
document.addEventListener("mousemove", moveSteer);
document.addEventListener("touchmove", moveSteer);
document.addEventListener("mouseup", stopSteer);
document.addEventListener("touchend", stopSteer);

function getEventPos(e) {
  if (e.touches && e.touches.length) return {x: e.touches[0].clientX, y: e.touches[0].clientY};
  return {x: e.clientX, y: e.clientY};
}

function startSteer(e) {
  isSteering = true;
  const rect = canvas.getBoundingClientRect();
  const pos = getEventPos(e);
  const dx = pos.x - (rect.left + rect.width / 2);
  const dy = pos.y - (rect.top + rect.height / 2);
  lastAngle = Math.atan2(dy, dx) * (180 / Math.PI);
  e.preventDefault();
}

function moveSteer(e) {
  if (!isSteering) return;
  const rect = canvas.getBoundingClientRect();
  const pos = getEventPos(e);
  const dx = pos.x - (rect.left + rect.width / 2);
  const dy = pos.y - (rect.top + rect.height / 2);
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);
  let delta = angle - lastAngle;
  if (delta > 180) delta -= 360;
  if (delta < -180) delta += 360;
  steerAngle = Math.max(minLeft, Math.min(maxRight, steerAngle + delta));
  lastAngle = angle;
  drawWheel(steerAngle);
  document.getElementById("steerVal").textContent = Math.round(steerAngle) + "°";

  // Send steer after short delay
  clearTimeout(window.steerTimeout);
  window.steerTimeout = setTimeout(() => {
    fetch(baseURL + "/steer?val=" + Math.round(steerAngle))
      .catch(e => console.warn("Steer error:", e));
  }, 150);
}

function stopSteer() { isSteering = false; }

function toggleDirection() {
  direction = (direction === "forward") ? "backward" : "forward";
  const btn = document.getElementById("direction");
  btn.textContent = direction.charAt(0).toUpperCase() + direction.slice(1);
  btn.classList.toggle("backward", direction === "backward");
}

function accelerate() {
  fetch(baseURL + "/" + direction)
    .then(() => console.log("Accelerate", direction))
    .catch(e => alert("Error: " + e));
}

function brake() {
  steerAngle = 0;
  drawWheel(0);
  document.getElementById("steerVal").textContent = "0°";
  fetch(baseURL + "/stop")
    .then(() => console.log("Brake pressed"))
    .catch(e => alert("Error: " + e));
}
