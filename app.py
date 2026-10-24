import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="F1 Pro Racer", page_icon="🏎️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    h1 { color: #e10600; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🏎️ F1 PADDOCK PRO RACER")
st.write("<p style='text-align: center;'>Use on-screen touch buttons or keyboard arrows to dodge rival cars!</p>", unsafe_allow_html=True)

game_code = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { background: #0b0e14; color: white; text-align: center; font-family: sans-serif; margin: 0; padding: 0; }
  canvas { background: #1a1d24; border: 3px solid #e10600; box-shadow: 0 0 25px rgba(225,6,0,0.5); display: block; margin: 0 auto; border-radius: 8px; }
  .controls { margin-top: 15px; display: flex; justify-content: center; gap: 20px; }
  button { background: #e10600; color: white; border: none; padding: 15px 35px; font-size: 20px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
  button:active { background: #b50500; transform: scale(0.95); }
  .scoreboard { font-size: 18px; margin-bottom: 8px; font-weight: bold; color: #00ffcc; }
</style>
</head>
<body>
  <div class="scoreboard">Distance: <span id="score">0</span>m</div>
  <canvas id="gameCanvas" width="380" height="520"></canvas>
  <div class="controls">
    <button id="leftBtn">◀ STEER</button>
    <button id="rightBtn">STEER ▶</button>
  </div>

  <script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    let car = { x: 170, y: 410, width: 40, height: 75, speed: 7 };
    let obstacles = [];
    let score = 0;
    let gameOver = false;
    let keys = {};
    let roadOffset = 0;

    window.addEventListener('keydown', e => keys[e.key] = true);
    window.addEventListener('keyup', e => keys[e.key] = false);

    // Touch controls
    const leftBtn = document.getElementById('leftBtn');
    const rightBtn = document.getElementById('rightBtn');

    let leftPressed = false, rightPressed = false;

    leftBtn.addEventListener('touchstart', (e) => { e.preventDefault(); leftPressed = true; });
    leftBtn.addEventListener('touchend', (e) => { e.preventDefault(); leftPressed = false; });
    leftBtn.addEventListener('mousedown', () => leftPressed = true);
    leftBtn.addEventListener('mouseup', () => leftPressed = false);

    rightBtn.addEventListener('touchstart', (e) => { e.preventDefault(); rightPressed = true; });
    rightBtn.addEventListener('touchend', (e) => { e.preventDefault(); rightPressed = false; });
    rightBtn.addEventListener('mousedown', () => rightPressed = true);
    rightBtn.addEventListener('mouseup', () => rightPressed = false);

    function spawnObstacle() {
        if (gameOver) return;
        let lanes = [65, 140, 215, 290];
        let x = lanes[Math.floor(Math.random() * lanes.length)];
        let colors = ["#00d2be", "#dc0000", "#ff8700", "#229954", "#3498db"];
        let color = colors[Math.floor(Math.random() * colors.length)];
        obstacles.push({ x: x, y: -90, width: 40, height: 75, speed: 6, color: color });
    }

    setInterval(spawnObstacle, 1300);

    function drawF1Car(x, y, color, isPlayer) {
        ctx.save();
        ctx.translate(x, y);

        // Tires
        ctx.fillStyle = "#111";
        ctx.fillRect(-6, 8, 8, 18);
        ctx.fillRect(38, 8, 8, 18);
        ctx.fillRect(-6, 48, 8, 18);
        ctx.fillRect(38, 48, 8, 18);

        // Front Wing
        ctx.fillStyle = isPlayer ? "#ffffff" : "#444";
        ctx.fillRect(2, 0, 36, 6);

        // Nose Cone & Cockpit
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.moveTo(20, 6);
        ctx.lineTo(12, 30);
        ctx.lineTo(28, 30);
        ctx.closePath();
        ctx.fill();

        // Sidepods & Body
        ctx.fillRect(8, 25, 24, 38);

        // Driver Helmet
        ctx.fillStyle = isPlayer ? "#ffcc00" : "#ffffff";
        ctx.beginPath();
        ctx.arc(20, 36, 5, 0, Math.PI * 2);
        ctx.fill();

        // Rear Wing
        ctx.fillStyle = isPlayer ? "#e10600" : "#222";
        ctx.fillRect(4, 66, 32, 6);

        ctx.restore();
    }

    function update() {
        if (gameOver) return;

        roadOffset = (roadOffset + 6) % 40;

        if ((keys['ArrowLeft'] || keys['a'] || leftPressed) && car.x > 45) car.x -= car.speed;
        if ((keys['ArrowRight'] || keys['d'] || rightPressed) && car.x < 295) car.x += car.speed;

        for (let i = obstacles.length - 1; i >= 0; i--) {
            obstacles[i].y += obstacles[i].speed;

            // Collision check
            if (
                car.x < obstacles[i].x + obstacles[i].width - 5 &&
                car.x + car.width > obstacles[i].x + 5 &&
                car.y < obstacles[i].y + obstacles[i].height - 5 &&
                car.y + car.height > obstacles[i].y + 5
            ) {
                gameOver = true;
            }

            if (obstacles[i].y > 550) {
                obstacles.splice(i, 1);
                score += 15;
                document.getElementById("score").innerText = score;
            }
        }
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Asphalt Road
        ctx.fillStyle = "#2c3e50";
        ctx.fillRect(40, 0, 300, canvas.height);

        // Red/White Curbs
        for (let y = -40 + roadOffset; y < canvas.height; y += 40) {
            ctx.fillStyle = "#e10600";
            ctx.fillRect(30, y, 10, 20);
            ctx.fillRect(340, y, 10, 20);
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(30, y + 20, 10, 20);
            ctx.fillRect(340, y + 20, 10, 20);
        }

        // Center dashed lines
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 3;
        ctx.setLineDash([20, 20]);
        ctx.lineDashOffset = -roadOffset * 1.5;
        ctx.beginPath();
        ctx.moveTo(130, 0); ctx.lineTo(130, canvas.height);
        ctx.moveTo(250, 0); ctx.lineTo(250, canvas.height);
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw Rival Cars
        obstacles.forEach(obs => {
            drawF1Car(obs.x, obs.y, obs.color, false);
        });

        // Draw Player F1 Car (Ferrari Red)
        drawF1Car(car.x, car.y, "#e10600", true);

        if (gameOver) {
            ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "#e10600";
            ctx.font = "bold 26px sans-serif";
            ctx.fillText("CRASH! RED FLAG", 75, 230);
            ctx.fillStyle = "#ffffff";
            ctx.font = "16px sans-serif";
            ctx.fillText("Final Distance: " + score + "m", 120, 270);
            ctx.fillStyle = "#00ffcc";
            ctx.fillText("Refresh page to race again", 90, 310);
        }
    }

    function loop() {
        update();
        draw();
        requestAnimationFrame(loop);
    }

    loop();
  </script>
</body>
</html>
"""

components.html(game_code, height=640)
