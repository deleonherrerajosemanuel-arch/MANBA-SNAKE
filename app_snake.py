import streamlit as st
import streamlit.components.v1 as components
import random
import csv
import os

# --- Lógica del Juego ---

def crear_matriz_vacia():
    return [[0 for _ in range(10)] for _ in range(10)]

def colocar_comida(matriz):
    vacias = [(r, c) for r in range(10) for c in range(10) if matriz[r][c] == 0]
    if vacias:
        r, c = random.choice(vacias)
        matriz[r][c] = -1

def inicializar_juego():
    matriz = crear_matriz_vacia()
    matriz[5][5] = 1 
    matriz[5][4] = 2 
    matriz[5][3] = 3 
    colocar_comida(matriz)
    return matriz

def obtener_puntaje(matriz):
    if not matriz: return 0
    return sum(1 for fila in matriz for celda in fila if celda > 0) - 3

def procesar_movimiento(matriz, direccion):
    hr, hc = -1, -1
    for r in range(10):
        for c in range(10):
            if matriz[r][c] == 1:
                hr, hc = r, c
                break
                
    dr, dc = 0, 0
    if direccion == 'W': dr = -1
    elif direccion == 'S': dr = 1
    elif direccion == 'A': dc = -1
    elif direccion == 'D': dc = 1
    
    nr, nc = hr + dr, hc + dc
    
    if not (0 <= nr < 10 and 0 <= nc < 10):
        return False, "Chocaste con el borde.", "crash"
    if matriz[nr][nc] > 0:
        return False, "Chocaste contigo mismo.", "crash"
        
    comio = (matriz[nr][nc] == -1)
    
    for r in range(10):
        for c in range(10):
            if matriz[r][c] > 0:
                matriz[r][c] += 1
                
    evento = "none"
    if not comio:
        max_val = 0
        tr, tc = -1, -1
        for r in range(10):
            for c in range(10):
                if matriz[r][c] > max_val:
                    max_val = matriz[r][c]
                    tr, tc = r, c
        if tr != -1:
            matriz[tr][tc] = 0
    else:
        colocar_comida(matriz)
        evento = "eat"
        
    matriz[nr][nc] = 1
    return True, "", evento

def guardar_partida(matriz):
    with open('partida.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(matriz)

def cargar_partida():
    if not os.path.exists('partida.csv'):
        return None
    try:
        matriz = []
        with open('partida.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    matriz.append([int(x) for x in row])
        if len(matriz) == 10 and all(len(row) == 10 for row in matriz):
            return matriz
    except:
        pass
    return None

# --- Interfaz de Streamlit ---

st.title("🐍 Snake por Turnos (Manba V2 Support)")

if 'matriz' not in st.session_state:
    st.session_state.matriz = None
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'mensaje' not in st.session_state:
    st.session_state.mensaje = ""
if 'evento' not in st.session_state:
    st.session_state.evento = "none"

if st.session_state.matriz is None:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Nueva Partida", use_container_width=True):
            st.session_state.matriz = inicializar_juego()
            st.session_state.game_over = False
            st.session_state.mensaje = ""
            st.session_state.evento = "none"
            st.rerun()
    with col2:
        if st.button("Reanudar Partida", use_container_width=True):
            cargada = cargar_partida()
            if cargada:
                st.session_state.matriz = cargada
                st.session_state.game_over = False
                st.session_state.mensaje = ""
                st.session_state.evento = "none"
                st.rerun()
            else:
                st.error("No se encontró partida guardada.")
else:
    puntaje = obtener_puntaje(st.session_state.matriz)
    st.subheader(f"Puntos: {puntaje}")
    
    if st.session_state.mensaje:
        if st.session_state.game_over:
            st.error(st.session_state.mensaje)
        else:
            st.success(st.session_state.mensaje)

    tablero_str = ""
    for fila in st.session_state.matriz:
        for celda in fila:
            if celda == 0: tablero_str += ".  "
            elif celda == -1: tablero_str += "🍎 "
            elif celda == 1: tablero_str += "🟩 "
            else: tablero_str += "🟩 "
        tablero_str += "\n"
        
    st.markdown(f"""
        <div style='font-family: monospace; font-size: 20px; line-height: 1.5; text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 10px;'>
            {tablero_str.replace(' ', '&nbsp;').replace(chr(10), '<br>')}
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.game_over:
        st.write("---")
        col_vacia1, col_arriba, col_vacia2, col_guardar = st.columns([1, 1, 1, 2])
        with col_arriba:
            btn_w = st.button("⬆️ W", use_container_width=True)
        with col_guardar:
            btn_g = st.button("💾 Guardar y Salir", use_container_width=True)
            
        col_izq, col_abajo, col_der, col_vacia3 = st.columns([1, 1, 1, 2])
        with col_izq:
            btn_a = st.button("⬅️ A", use_container_width=True)
        with col_abajo:
            btn_s = st.button("⬇️ S", use_container_width=True)
        with col_der:
            btn_d = st.button("➡️ D", use_container_width=True)

        direccion = None
        if btn_w: direccion = 'W'
        elif btn_s: direccion = 'S'
        elif btn_a: direccion = 'A'
        elif btn_d: direccion = 'D'
        
        if direccion:
            exito, msg, evento = procesar_movimiento(st.session_state.matriz, direccion)
            st.session_state.evento = evento
            if not exito:
                st.session_state.game_over = True
                st.session_state.mensaje = f"Fin del juego. {msg}"
            st.rerun()
        else:
            st.session_state.evento = "none"
            
        if btn_g:
            guardar_partida(st.session_state.matriz)
            st.session_state.matriz = None
            st.session_state.mensaje = "Partida guardada correctamente."
            st.rerun()
            
    if st.session_state.game_over:
        if st.button("Volver al Menú"):
            st.session_state.matriz = None
            st.rerun()

# --- Conexión Nativa para Mando y Hápticos ---
js_code = f"""
<script>
(function() {{
    const topWin = window.parent;
    const doc = topWin.document;
    const currentEvent = "{st.session_state.evento}";

    // Sistema de Vibración Nivel 2
    function triggerHaptic(type) {{
        const gps = (navigator.getGamepads ? navigator.getGamepads() : []) || [];
        for (let gp of gps) {{
            if (gp && gp.vibrationActuator) {{
                if (type === 'eat') {{
                    gp.vibrationActuator.playEffect("dual-rumble", {{
                        startDelay: 0, duration: 180, weakMagnitude: 0.8, strongMagnitude: 0.2
                    }});
                }} else if (type === 'crash') {{
                    gp.vibrationActuator.playEffect("dual-rumble", {{
                        startDelay: 0, duration: 600, weakMagnitude: 1.0, strongMagnitude: 1.0
                    }});
                }}
            }}
        }}
    }}

    if (currentEvent !== "none") {{
        triggerHaptic(currentEvent);
    }}

    // Bucle Global en la Ventana Principal para evitar el aislamiento del Iframe
    if (!topWin.manbaLoopRunning) {{
        topWin.manbaLoopRunning = true;
        let lastPressTime = 0;

        function gameLoop() {{
            const gps = (topWin.navigator.getGamepads ? topWin.navigator.getGamepads() : []) || [];
            let gp = null;
            for (let g of gps) {{
                if (g) {{ gp = g; break; }}
            }}

            if (gp) {{
                const now = Date.now();
                if (now - lastPressTime > 220) {{
                    const buttons = Array.from(doc.querySelectorAll('button'));
                    const btnW = buttons.find(el => el.innerText.includes('W'));
                    const btnA = buttons.find(el => el.innerText.includes('A'));
                    const btnS = buttons.find(el => el.innerText.includes('S'));
                    const btnD = buttons.find(el => el.innerText.includes('D'));

                    let pressed = false;

                    // Mapeo XInput/DirectInput para Manba V2 (Cruceta + Joystick)
                    const upPressed = (gp.buttons[12] && gp.buttons[12].pressed) || (gp.axes[1] && gp.axes[1] < -0.4);
                    const downPressed = (gp.buttons[13] && gp.buttons[13].pressed) || (gp.axes[1] && gp.axes[1] > 0.4);
                    const leftPressed = (gp.buttons[14] && gp.buttons[14].pressed) || (gp.axes[0] && gp.axes[0] < -0.4);
                    const rightPressed = (gp.buttons[15] && gp.buttons[15].pressed) || (gp.axes[0] && gp.axes[0] > 0.4);

                    if (upPressed && btnW) {{ btnW.click(); pressed = true; }}
                    else if (downPressed && btnS) {{ btnS.click(); pressed = true; }}
                    else if (leftPressed && btnA) {{ btnA.click(); pressed = true; }}
                    else if (rightPressed && btnD) {{ btnD.click(); pressed = true; }}

                    if (pressed) lastPressTime = now;
                }}
            }}
            topWin.requestAnimationFrame(gameLoop);
        }}
        topWin.requestAnimationFrame(gameLoop);
    }}
}})();
</script>
"""
components.html(js_code, height=0, width=0)
