# Chess Engine

Real-time multiplayer chess with a Python backend and React frontend. Two players connect to a room from the browser and play via WebSockets, with server-side clocks and anti-cheat enforcement.

## Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite, WebSockets
- **Frontend:** React
- **Engine:** custom chess logic in pure Python, no external libraries

## Features

- Real-time multiplayer via WebSockets
- Room lobby: browse open games, create a room with a comment and time control, join as white, black, or spectator
- Per-player clock (configurable), managed server-side — clients cannot manipulate time
- Token-based auth: secret token issued on join, validated on every WebSocket message
- Turn enforcement: server rejects moves from the wrong player or spectators
- Check, checkmate, and stalemate detection
- Castling, en passant, and pawn promotion
- Resign and draw offer (with accept/reject flow)
- Move history in SAN notation with interactive navigation
- Drag & drop pieces
- Board flip (black's perspective)
- Move sound effect
- Full persistence: FEN + move history saved to DB, game recovers after server restart

## Structure

```
chess-engine/
  ├── engine/               ← pure chess logic (board.py, game.py, pieces.py)
  ├── server/
  │   ├── main.py
  │   ├── database.py
  │   ├── models.py
  │   ├── schemas.py
  │   └── routers/
  │       ├── rooms.py      ← REST: list, create, get, join rooms
  │       └── websocket.py  ← WS: moves, timer, broadcast, game actions
  └── web/
      └── src/
          ├── App.js        ← game board
          └── Lobby.js      ← room list and join flow
```

## Setup

**Backend**
```bash
# Activate the virtualenv (lives in core/venv)
core\venv\Scripts\Activate.ps1    # Windows PowerShell
source core/venv/bin/activate     # Linux / Mac

pip install -r requirements.txt
uvicorn server.main:app --reload
```

**Frontend**
```bash
cd web
npm install
npm start
```

The SQLite database (`test.db`) is created automatically on first server start.

## Usage

1. Open `http://localhost:3000`
2. Enter a nickname
3. Create a room or join an existing one, pick a color
4. Share the room with your opponent — the clock starts when both players have joined
