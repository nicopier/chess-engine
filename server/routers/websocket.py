import time
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from engine.game import Game
from ..database import SessionLocal
from ..models import Room


class ConnectionManager:
    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = {}
        self.games: dict[str, Game] = {}
        self.locks: dict[str, asyncio.Lock] = {}
        self.timer_tasks: dict[str, asyncio.Task] = {}

    def connect(self, room_id: str, websocket: WebSocket):
        if room_id not in self.rooms:
            self.rooms[room_id] = []
        self.rooms[room_id].append(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        self.rooms[room_id].remove(websocket)

    def get_game(self, room_id: str, fen: str, move_history: list = None) -> Game:
        if room_id not in self.games:
            self.games[room_id] = Game(fen, move_history=move_history or [])
            self.locks[room_id] = asyncio.Lock()
        return self.games[room_id]

    async def broadcast(self, room_id: str, message: str):
        for ws in list(self.rooms.get(room_id, [])):
            try:
                await ws.send_text(message)
            except Exception:
                pass


def build_state(game, room=None, success=True):
    board_state = [
        {"type": p.piece_type.value, "color": p.color.value, "position": list(p.position)}
        for row in game.board.board for p in row if p is not None
    ]
    now = time.time()
    time_white = room.time_white if room else None
    time_black = room.time_black if room else None
    if room and room.status == "playing" and room.last_move_at:
        elapsed = now - room.last_move_at
        if game.current_turn.value == "white":
            time_white = max(0.0, room.time_white - elapsed)
        else:
            time_black = max(0.0, room.time_black - elapsed)
    return {
        "success": success,
        "board": board_state,
        "turn": game.current_turn.value,
        "white_in_check": game.white_in_check,
        "black_in_check": game.black_in_check,
        "history": game.move_history,
        "time_white": time_white,
        "time_black": time_black,
        "player_white": room.player_white if room else None,
        "player_black": room.player_black if room else None,
    }


async def end_game_broadcast(room_id: str, game: Game, room, result: str, reason: str, db):
    game.end_game(result)
    room.status = "finished"
    db.commit()
    await manager.broadcast(room_id, json.dumps({
        **build_state(game, room),
        "game_over": True,
        "result": result,
        "reason": reason,
    }))


async def timer_loop(room_id: str):
    while True:
        await asyncio.sleep(1)
        db = SessionLocal()
        try:
            room = db.query(Room).filter(Room.id == room_id).first()
            if not room or room.status != "playing":
                break
            game = manager.games.get(room_id)
            if not game:
                break
            now = time.time()
            elapsed = now - room.last_move_at
            if game.current_turn.value == "white":
                remaining = room.time_white - elapsed
            else:
                remaining = room.time_black - elapsed
            if remaining <= 0:
                if game.current_turn.value == "white":
                    room.time_white = 0
                    result = "black_wins"
                else:
                    room.time_black = 0
                    result = "white_wins"
                await end_game_broadcast(room_id, game, room, result, "timeout", db)
                break
            await manager.broadcast(room_id, json.dumps(build_state(game, room)))
        finally:
            db.close()


manager = ConnectionManager()
router = APIRouter()


@router.websocket("/rooms/{room_id}/ws")
async def websocket_endpoint(room_id: str, websocket: WebSocket, token: str = None):
    await websocket.accept()
    manager.connect(room_id, websocket)
    db = SessionLocal()
    try:
        room = db.query(Room).filter(Room.id == room_id).first()
        saved_history = json.loads(room.history) if room.history else []
        fen = saved_history[-1]["fen"] if saved_history else room.fen
        game = manager.get_game(room_id, fen, saved_history)

        # determinar color del jugador una sola vez al conectarse
        if token and token == room.white_token:
            player_color = "white"
        elif token and token == room.black_token:
            player_color = "black"
        else:
            player_color = None  # espectador

        await websocket.send_text(json.dumps(build_state(game, room)))
        if room.status == "playing" and room_id not in manager.timer_tasks:
            manager.timer_tasks[room_id] = asyncio.create_task(timer_loop(room_id))

        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if "action" in msg:
                if player_color is None:
                    continue
                action = msg["action"]

                if action == "resign":
                    result = "black_wins" if player_color == "white" else "white_wins"
                    room = db.query(Room).filter(Room.id == room_id).first()
                    await end_game_broadcast(room_id, game, room, result, "resign", db)

                elif action == "offer_draw":
                    await manager.broadcast(room_id, json.dumps({"draw_offer": player_color}))

                elif action == "accept_draw":
                    room = db.query(Room).filter(Room.id == room_id).first()
                    await end_game_broadcast(room_id, game, room, "draw", "agreement", db)

                elif action == "reject_draw":
                    await manager.broadcast(room_id, json.dumps({"draw_rejected": True}))

            else:
                # movimiento — validar turno
                if player_color is None or player_color != game.current_turn.value:
                    continue
                async with manager.locks[room_id]:
                    result = await asyncio.to_thread(
                        game.make_move,
                        tuple(msg["from_pos"]), tuple(msg["to_pos"]), msg.get("promotion")
                    )
                if result:
                    now = time.time()
                    room = db.query(Room).filter(Room.id == room_id).first()
                    if room.last_move_at is not None:
                        elapsed = now - room.last_move_at
                        if game.current_turn.value == "black":
                            room.time_white = max(0.0, room.time_white - elapsed)
                        else:
                            room.time_black = max(0.0, room.time_black - elapsed)
                    room.last_move_at = now
                    room.fen = game.board.to_fen(game.current_turn, game.en_passant_target, game.halfmove_clock, game.fullmove_number)
                    room.history = json.dumps(game.move_history)
                    if game.game_over:
                        room.status = "finished"
                    db.commit()

                state = build_state(game, room, result)
                if result:
                    state["moved"] = True
                if game.game_over:
                    state["game_over"] = True
                    state["result"] = game.result
                    state["reason"] = game.game_over_reason
                await manager.broadcast(room_id, json.dumps(state))

    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
    finally:
        db.close()
