import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="F1 Arcade Game", page_icon="🏎️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    h1 { color: #e10600; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🏎️ F1 RETRO ARCADE RACER")
st.write("<p style='text-align: center;'>Use <b>A / D</b> or <b>Left / Right Arrows</b> to steer and dodge rivals!</p>", unsafe_allow_html=True)

# Embedded HTML5/JS Racing Canvas Game
game_code = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { background: #111; color: white; text-align: center; font-family: sans-serif; margin: 0; }
  canvas { background: #222; border: 3px solid #e10600; box-shadow: 0 0 20px #e10600; display: block; margin: 0 auto; }
</style>
</head>
<body>
  <h2>Score: <span id="score">0</span></h2>
  <canvas id="gameCanvas" width="400" height="500"></canvas>
  <script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    let car = { x: 180, y: 400, width: 40, height: 70, speed: 6 };
    let obstacles = [];
    let score = 0;
    let gameOver = false;
    let keys = {};

    window.addEventListener('keydown', e => keys[e.key] = true);
    window.addEventListener('keyup', e => keys[e.key] = false);

    function spawnObstacle() {
        if (gameOver) return;
        let xPositions = [50, 140, 230, 310];
        let x = xPositions[Math.floor(Math.random() * xPositions.length)];
        obstacles.push({ x: x, y: -80, width: 40, height: 70, speed: 5 });
    }

    setInterval(spawnObstacle, 1200);

    function update() {
        if (gameOver) return;

        if ((keys['ArrowLeft'] || keys['a'] || keys['A']) && car.x > 30) car.x -= car.speed;
        if ((keys['ArrowRight'] || keys['d'] || keys['D']) && car.x < 330) car.x += car.speed;

        for (let i = obstacles.length - 1; i >= 0; i--) {
            obstacles[i].y += obstacles[i].speed;

            // Collision Detection
            if (
                car.x < obstacles[i].x + obstacles[i].width &&
                car.x + car.width > obstacles[i].x &&
                car.y < obstacles[i].y + obstacles[i].height &&
                car.y + car.height > obstacles[i].y
            ) {
                gameOver = true;
            }

            if (obstacles[i].y > 550) {
                obstacles.splice(i, 1);
                score += 10;
                document.getElementById("score").innerText = score;
            }
        }
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Road lanes
        ctx.strokeStyle = "#fff";
        ctx.setLineDash([20, 20]);
        ctx.beginPath();
        ctx.moveTo(133, 0); ctx.lineTo(133, 500);
        ctx.moveTo(266, 0); ctx.lineTo(266, 500);
        ctx.stroke();

        // Player F1 Car
        ctx.fillStyle = "#e10600";
        ctx.fillRect(car.x, car.y, car.width, car.height);
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(car.x + 12, car.y + 25, 16, 20);

        // Rival Cars
        ctx.fillStyle = "#0055ff";
        obstacles.forEach(obs => {
            ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
            ctx.fillStyle = "#ffcc00";
            ctx.fillRect(obs.x + 12, obs.y + 25, 16, 20);
            ctx.fillStyle = "#0055ff";
        });

        if (gameOver) {
            ctx.fillStyle = "rgba(0,0,0,0.85)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "#e10600";
            ctx.font = "bold 26px sans-serif";
            ctx.fillText("CRASH! GAME OVER", 65, 240);
            ctx.fillStyle = "#ffffff";
            ctx.font = "16px sans-serif";
            ctx.fillText("Refresh page to race again", 105, 280);
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

components.html(game_code, height=600)
