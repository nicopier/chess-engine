# Chess Engine

A fully custom multiplayer chess game built from scratch — no chess libraries, no shortcuts. The engine, the rules, the server, and the client are all hand-rolled.

Two players open a browser, join a room, and play in real time. The server owns everything: the game state, the clock, the move validation. Clients just send inputs and render what they receive.

---

## How it works

**The engine** (`engine/`) is pure Python with zero dependencies. It implements the full ruleset: legal move generation, check detection, checkmate, castling, en passant, and pawn promotion. Board state is stored and transmitted as FEN strings.

**The server** (`server/`) is a FastAPI app that manages rooms, persists state to SQLite, and communicates with clients over WebSockets. Every move is validated server-side — the client has no authority over game state or time.

**The frontend** (`web/`) is a React app. The board connects to a WebSocket on mount and reacts to server broadcasts. No polling, no REST calls mid-game.

---

## Features

- Custom chess engine written in pure Python
- Real-time multiplayer via WebSockets
- Room lobby — browse open games, see who created them, join or spectate
- Per-player clock with configurable time control (1 min to 30 min)
- Server-side timer — completely anti-cheat, clients cannot influence time
- Token-based authentication — secret token issued on join, validated on every WebSocket message
- Turn enforcement — server ignores moves from the wrong player or spectators
- Spectator mode — watch any live game without affecting it
- Resign and draw offer with accept/reject flow
- Check, checkmate detection
- Castling, en passant, pawn promotion
- Move history in SAN notation with full board replay navigation
- Drag & drop pieces (pure mouse events, no HTML5 DnD)
- Board flip for black's perspective
- Move sound effect
- Full persistence — FEN and move history saved to DB after every move, game fully recovers after server restart

---

## Stack

| Layer | Tech |
|---|---|
| Chess engine | Python (pure, no libs) |
| Backend | FastAPI, SQLAlchemy, SQLite |
| Real-time | WebSockets (native FastAPI) |
| Frontend | React |

---

## Project structure

```
chess-engine/
  ├── engine/
  │   ├── pieces.py         ← piece classes, move generation
  │   ├── board.py          ← board state, FEN parsing/generation, SAN notation
  │   └── game.py           ← game loop, move validation, checkmate detection
  ├── server/
  │   ├── main.py           ← FastAPI app entry point
  │   ├── database.py       ← SQLAlchemy engine and session
  │   ├── models.py         ← Room ORM model
  │   ├── schemas.py        ← Pydantic request/response schemas
  │   └── routers/
  │       ├── rooms.py      ← REST: list, create, get, join rooms
  │       └── websocket.py  ← WebSocket endpoint, ConnectionManager, timer loop
  └── web/
      └── src/
          ├── App.js        ← game board, WebSocket client, all game UI
          └── Lobby.js      ← room list, create modal, join/spectate flow
```

---

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

The SQLite database (`test.db`) is created automatically on first server start. If you change the DB schema, stop the server, delete `test.db`, and restart.

---

## How to play

1. Open `http://localhost:3000`
2. Enter a nickname
3. Create a room — pick a comment and time control
4. Share the room link or just tell your opponent to open the same URL and join
5. The clock starts the moment both players have joined
6. Spectators can join any room at any time and watch live

---

## Design decisions

**No client authority.** The client sends `from` and `to` positions. The server validates the move against the engine, updates the clock, saves state to the DB, and broadcasts the new state to all connections in the room. The client never tells the server what the board looks like — only what the player wants to do.

**Anti-cheat timer.** Time is stored as `(time_remaining, last_move_at)` in the DB. The actual remaining time is computed as `time_remaining - (now - last_move_at)` on every broadcast. Pausing the browser, throttling the network, or manipulating localStorage has zero effect.

**Token auth.** When a player joins a room, the server generates a random UUID token and returns it once. The client passes it as a WebSocket query param. The server maps the token to a color (white/black) — no token means spectator. Someone who sniffs the WebSocket URL only sees their own token, not the opponent's.

**FEN + history persistence.** After every move, the server saves the full FEN and the complete move history (as JSON) to the DB. If the server crashes mid-game, the game is fully reconstructed from the DB on the next connection — board position, move list, and remaining time.
