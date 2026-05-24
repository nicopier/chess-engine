# Chess Engine

Motor de ajedrez multiplayer con backend Python y frontend React. Dos jugadores se conectan a una sala desde el navegador y juegan en tiempo real via WebSockets, con reloj por jugador gestionado en el servidor.

## Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite, WebSockets
- **Frontend:** React
- **Engine:** lógica de ajedrez propia en Python puro (sin librerías externas)

## Features

- Multiplayer en tiempo real via WebSockets
- Lobby: crear sala con código, elegir color, unirse con nickname
- Reloj por jugador (configurable), gestionado server-side (anti-cheat)
- Detección de jaque, jaque mate y promoción de peones
- Castling y en passant
- Historial de movimientos en notación SAN con navegación interactiva
- Drag & drop de piezas
- Tablero rotable (perspectiva de negras)
- Persistencia: FEN + historial guardados en DB, la partida se recupera si el servidor reinicia

## Estructura

```
chess-engine/
  ├── engine/         ← lógica pura (board.py, game.py, pieces.py)
  ├── server/
  │   ├── main.py
  │   ├── database.py
  │   ├── models.py
  │   ├── schemas.py
  │   └── routers/
  │       ├── rooms.py      ← REST: crear/obtener/unirse a salas
  │       └── websocket.py  ← WS: movimientos, timer, broadcast
  └── web/
      └── src/
          ├── App.js        ← tablero
          └── Lobby.js      ← pantalla de inicio
```

## Cómo levantar

**Backend**
```bash
# Activar el venv (está en core/venv)
core\venv\Scripts\Activate.ps1       # Windows PowerShell
# o
source core/venv/bin/activate        # Linux/Mac

pip install -r requirements.txt
uvicorn server.main:app --reload
```

**Frontend**
```bash
cd web
npm install
npm start
```

La DB (`test.db`) se crea sola al levantar el server.

## Uso

1. Abrir `http://localhost:3000`
2. Entrar como invitado, escribir un nickname
3. Crear una sala (o unirse con el código de una existente) y elegir color
4. Compartir el código de sala al otro jugador
5. Cuando los dos están conectados, empieza el reloj y pueden jugar
