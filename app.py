import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="F1 Pseudo-3D Racer", page_icon="🏎️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    h1 { color: #e10600; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🏎️ MONOPOSTO-STYLE 3D F1 RACER")
st.write("<p style='text-align: center;'>Curved track, 3D perspective, touch controls & steering!</p>", unsafe_allow_html=True)

game_code = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { background: #0b0e14; color: white; text-align: center; font-family: sans-serif; margin: 0; padding: 0; overflow: hidden; }
  canvas { background: #338833; border: 3px solid #e10600; box-shadow: 0 0 25px rgba(225,6,0,0.6); display: block; margin: 0 auto; border-radius: 8px; }
  .controls { margin-top: 10px; display: flex; justify-content: center; gap: 15px; }
  button { background: #e10600; color: white; border: none; padding: 12px 25px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.3); user-select: none; }
  button:active { background: #b50500; transform: scale(0.95); }
  .dash { font-size: 16px; margin-bottom: 6px; font-weight: bold; color: #00ffcc; display: flex; justify-content: center; gap: 20px; }
</style>
</head>
<body>
  <div class="dash">
    <div>SPEED: <span id="speed">240</span> KM/H</div>
    <div>GEAR: <span id="gear">5</span></div>
  </div>
  <canvas id="gameCanvas" width="400" height="480"></canvas>
  <div class="controls">
    <button id="leftBtn">◀ LEFT</button>
    <button id="brakeBtn">BRAKE</button>
    <button id="accelBtn">ACCEL</button>
    <button id="rightBtn">RIGHT ▶</button>
  </div>

  <script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    let playerX = 0; // -2 to 2 road position
    let speed = 0;
    let maxSpeed = 200;
    let position = 0;
    let carX = 200;
    
    let keys = {};
    let leftPressed = false, rightPressed = false, accelPressed = true, brakePressed = false;

    window.addEventListener('keydown', e => keys[e.key] = true);
    window.addEventListener('keyup', e => keys[e.key] = false);

    // Touch setup
    const bindTouch = (id, setter) => {
        const el = document.getElementById(id);
        el.addEventListener('touchstart', e => { e.preventDefault(); setter(true); });
        el.addEventListener('touchend', e => { e.preventDefault(); setter(false); });
        el.addEventListener('mousedown', () => setter(true));
        el.addEventListener('mouseup', () => setter(false));
    };

    bindTouch('leftBtn', v => leftPressed = v);
    bindTouch('rightBtn', v => rightPressed = v);
    bindTouch('accelBtn', v => accelPressed = v);
    bindTouch('brakeBtn', v => brakePressed = v);

    // Track geometry (pseudo-3D segments)
    const segL = 200;
    const totalSegments = 300;
    let lines = [];

    for(let i=0; i<totalSegments; i++) {
        let curve = Math.sin(i / 20) * 1.5;
        if(i > 100 && i < 150) curve = 2.5; // sharp turn
        if(i > 200 && i < 250) curve = -2.0;
        lines.push({
            index: i,
            p1: { world: { z: (i+1)*segL }, screen: {} },
            p2: { world: { z: i*segL }, screen: {} },
            curve: curve,
            color: Math.floor(i/3)%2 ? {road: '#444', grass: '#2e7d32', rumble: '#e10600'} : {road: '#4a4a4a', grass: '#388e3c', rumble: '#fff'}
        });
    }

    function update() {
        if (accelPressed || keys['ArrowUp'] || keys['w']) speed = Math.min(speed + 2, maxSpeed);
        else speed = Math.max(speed - 3, 0);

        if (brakePressed || keys['ArrowDown'] || keys['s']) speed = Math.max(speed - 8, 0);

        let turnRate = 0.03 * (speed / maxSpeed);
        if (leftPressed || keys['ArrowLeft'] || keys['a']) playerX -= turnRate;
        if (rightPressed || keys['ArrowRight'] || keys['d']) playerX += turnRate;

        position += speed;
        while (position >= totalSegments * segL) position -= totalSegments * segL;

        document.getElementById("speed").innerText = Math.floor(speed * 1.2);
        document.getElementById("gear").innerText = speed > 150 ? 5 : (speed > 100 ? 4 : (speed > 50 ? 3 : 2));
    }

    function render() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Sky & Horizon
        ctx.fillStyle = "#6bb2ff";
        ctx.fillRect(0, 0, canvas.width, 180);
        ctx.fillStyle = "#228b22";
        ctx.fillRect(0, 180, canvas.width, 300);

        let baseSegment = Math.floor(position / segL) % totalSegments;
        let basePercent = (position % segL) / segL;

        let maxY = 180;
        let x = 0, dx = 0;

        // Draw Road from back to front
        for(let n = 0; n < 100; n++) {
            let index = (baseSegment + n) % totalSegments;
            let line = lines[index];
            
            let current_z = line.p1.world.z - (position % segL);
            if (current_z <= 0) current_z += totalSegments * segL;

            let scale = 200 / current_z;
            let screenX = canvas.width/2 + (scale * line.p1.world.x) - (scale * playerX * 800);
            let screenY = canvas.height/2 + 30 - (scale * 0); // camera height

            // project curved segments
            dx += line.curve;
            let p1 = { x: screenX, y: screenY, w: scale * 800 };
            
            // Render segment
            if (n > 0) {
                let prevLine = lines[(baseSegment + n - 1) % totalSegments];
                // Draw polygon
                ctx.fillStyle = line.color.grass;
                ctx.fillRect(0, prevLine.p2.screen.y || 180, canvas.width, (p1.y - (prevLine.p2.screen.y || 180)) + 1);

                // Road polygon
                ctx.fillStyle = line.color.road;
                ctx.beginPath();
                ctx.moveTo(prevLine.p2.screen.x - prevLine.p2.w/2, prevLine.p2.screen.y);
                ctx.lineTo(prevLine.p2.screen.x + prevLine.p2.w/2, prevLine.p2.screen.y);
                ctx.lineTo(p1.x + p1.w/2, p1.y);
                ctx.lineTo(p1.x - p1.w/2, p1.y);
                ctx.fill();

                // Rumblestrips
                ctx.fillStyle = line.color.rumble;
                ctx.beginPath();
                ctx.moveTo(prevLine.p2.screen.x - prevLine.p2.w/2, prevLine.p2.screen.y);
                ctx.lineTo(prevLine.p2.screen.x - prevLine.p2.w/2 - prevLine.p2.w*0.05, prevLine.p2.screen.y);
                ctx.lineTo(p1.x - p1.w/2 - p1.w*0.05, p1.y);
                ctx.lineTo(p1.x - p1.w/2, p1.y);
                ctx.fill();

                ctx.beginPath();
                ctx.moveTo(prevLine.p2.screen.x + prevLine.p2.w/2, prevLine.p2.screen.y);
                ctx.lineTo(prevLine.p2.screen.x + prevLine.p2.w/2 + prevLine.p2.w*0.05, prevLine.p2.screen.y);
                ctx.lineTo(p1.x + p1.w/2 + p1.w*0.05, p1.y);
                ctx.lineTo(p1.x + p1.w/2, p1.y);
                ctx.fill();
            }
            line.p1.screen = { x: p1.x, y: p1.y, w: p1.w };
            line.p2.screen = { x: p1.x, y: p1.y, w: p1.w };
        }

        // Draw Player F1 Car (Rear view perspective like Monoposto)
        let cx = canvas.width / 2 + (playerX * 30);
        let cy = 380;

        // Rear Wing
        ctx.fillStyle = "#e10600";
        ctx.fillRect(cx - 50, cy - 25, 100, 12);
        ctx.fillStyle = "#111";
        ctx.fillRect(cx - 35, cy - 18, 12, 18);
        ctx.fillRect(cx + 23, cy - 18, 12, 18);

        // Rear Tires
        ctx.fillStyle = "#1a1a1a";
        ctx.fillRect(cx - 75, cy - 10, 24, 55);
        ctx.fillRect(cx + 51, cy - 10, 24, 55);

        // Main Body & Cockpit
        ctx.fillStyle = "#1b5e20"; // British Racing Green F1
        ctx.beginPath();
        ctx.moveTo(cx - 25, cy - 15);
        ctx.lineTo(cx + 25, cy - 15);
        ctx.lineTo(cx + 15, cy + 75);
        ctx.lineTo(cx - 15, cy + 75);
        ctx.closePath();
        ctx.fill();

        // Helmet & Halo
        ctx.fillStyle = "#ffcc00";
        ctx.beginPath();
        ctx.arc(cx, cy + 15, 9, 0, Math.PI*2);
        ctx.fill();
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(cx, cy + 18, 11, Math.PI, 0, true);
        ctx.stroke();
    }

    function loop() {
        update();
        render();
        requestAnimationFrame(loop);
    }

    loop();
  </script>
</body>
</html>
"""

components.html(game_code, height=600)
