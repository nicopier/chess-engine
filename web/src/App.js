import { useState, useEffect, useRef } from 'react';
import Lobby from './Lobby';

function App() {
  const [session, setSession] = useState(null); // { roomId, playerId, color }
  const [roomData, setRoomData] = useState(null);
  const historyEndRef = useRef(null);
  const wsRef = useRef(null);
  const [board, setBoard] = useState([]);
  const [selectedPiece, setSelectedPiece] = useState(null);
  const [whiteInCheck, setWhiteInCheck] = useState(false);
  const [blackInCheck, setBlackInCheck] = useState(false);
  const [timeWhite, setTimeWhite] = useState(null);
  const [timeBlack, setTimeBlack] = useState(null);
  const [gameOver, setGameOver] = useState(null); // null | { result, reason }
  const [drawOffer, setDrawOffer] = useState(null); // null | 'white' | 'black'
  const [flipped, setFlipped] = useState(false);
  useEffect(() => { if (session) setFlipped(session.color === 'black'); }, [session]);
  const rows = flipped ? [0,1,2,3,4,5,6,7] : [7,6,5,4,3,2,1,0];
  const cols = flipped ? [7,6,5,4,3,2,1,0] : [0,1,2,3,4,5,6,7];
  const INITIAL_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w';
  const [history, setHistory] = useState([]);
  const [viewingIndex, setViewingIndex] = useState(null);
  const [viewingBoard, setViewingBoard] = useState(null);
  const [promotionPending, setPromotionPending] = useState(null);

  // Drag state: ref para datos del drag (no causa re-renders en mousemove)
  // dragPos state: solo para redibujar la pieza flotante
  const dragState = useRef(null);   // { piece, from: [row, col] }
  const [dragPos, setDragPos] = useState(null);  // { x, y } | null
  const moveSound = useRef(new Audio('/sounds/move-self.mp3'));

  // Registra/limpia los listeners de mouse solo cuando empieza o termina un drag
  useEffect(() => {
    if (!dragPos) return;

    const onMouseMove = (e) => {
      setDragPos({ x: e.clientX, y: e.clientY });
    };

    const onMouseUp = (e) => {
      const state = dragState.current;
      dragState.current = null;
      setDragPos(null);
      if (!state) return;

      // elementsFromPoint devuelve TODOS los elementos en ese punto (en orden de z-index).
      // elementFromPoint devuelve solo el más arriba — que puede ser la pieza flotante,
      // cuyo padre no tiene data-square. Por eso usamos la versión plural y buscamos.
      const elements = document.elementsFromPoint(e.clientX, e.clientY);
      const squareEl = elements.find(el => el.dataset?.square);
      if (!squareEl) return;

      const [toRow, toCol] = squareEl.dataset.square.split(',').map(Number);
      const { from, piece } = state;
      if (from[0] === toRow && from[1] === toCol) return;

      const isPromotion = piece.type === 'pawn' &&
        ((piece.color === 'white' && toRow === 7) ||
         (piece.color === 'black' && toRow === 0));
      if (isPromotion) {
        setPromotionPending({ from, to: [toRow, toCol], color: piece.color });
        setSelectedPiece(null);
        return;
      }
      setSelectedPiece(null);
      sendMove(from, [toRow, toCol]);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
    return () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [!!dragPos]);

  useEffect(() => {
    if (!session) return;
    const API = process.env.REACT_APP_API_URL;
    const WS = API.replace(/^http/, 'ws');
    fetch(`${API}/rooms/${session.roomId}`)
      .then(r => r.json())
      .then(setRoomData);
    const wsUrl = session.token
      ? `${WS}/rooms/${session.roomId}/ws?token=${session.token}`
      : `${WS}/rooms/${session.roomId}/ws`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.moved) { moveSound.current.currentTime = 0; moveSound.current.play().catch(() => {}); }
      if (data.player_white || data.player_black) setRoomData(prev => ({ ...prev, player_white: data.player_white, player_black: data.player_black }));
      setBoard(data.board);
      setWhiteInCheck(data.white_in_check);
      setBlackInCheck(data.black_in_check);
      setHistory(data.history);
      if (data.time_white != null) setTimeWhite(data.time_white);
      if (data.time_black != null) setTimeBlack(data.time_black);
      if (data.game_over) { setGameOver({ result: data.result, reason: data.reason }); setDrawOffer(null); }
      if (data.draw_offer) { setDrawOffer(data.draw_offer); return; }
      if (data.draw_rejected) { setDrawOffer(null); return; }
      setViewingBoard(null);
      setViewingIndex(null);
      setSelectedPiece(null);
    };
    return () => ws.close();
  }, [session]);

  useEffect(() => {
    if (historyEndRef.current) {
      historyEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [history]);

  function formatTime(secs) {
    if (secs == null) return '--:--';
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  function getPieceImage(piece) {
    const colorLetter = piece.color === 'white' ? 'w' : 'b';
    const typeLetter = {
      pawn: 'P', knight: 'N', bishop: 'B',
      rook: 'R', queen: 'Q', king: 'K'
    }[piece.type];
    return `/pieces/${colorLetter}${typeLetter}.svg`;
  }

  function getPieceAt(row, col) {
    const currentBoard = viewingBoard ?? board;
    return currentBoard.find(p => p.position[0] === row && p.position[1] === col);
  }

  function parseFen(fen) {
    const fenToType = {
      'p': 'pawn', 'r': 'rook', 'n': 'knight',
      'b': 'bishop', 'q': 'queen', 'k': 'king'
    };
    const pieces = [];
    const fenRows = fen.split(' ')[0].split('/');
    fenRows.forEach((row, rowIndex) => {
      const actualRow = 7 - rowIndex;
      let col = 0;
      for (const char of row) {
        if (isNaN(char)) {
          pieces.push({
            type: fenToType[char.toLowerCase()],
            color: char === char.toUpperCase() ? 'white' : 'black',
            position: [actualRow, col]
          });
          col++;
        } else {
          col += parseInt(char);
        }
      }
    });
    return pieces;
  }

  function resetGame() {
    // TODO: implementar reset por sala cuando tengamos el endpoint
  }

  function goToPosition(index) {
    if (index === null || index === history.length - 1) {
      setViewingIndex(null);
      setViewingBoard(null);
      return;
    }
    setViewingIndex(index);
    if (index === -1) {
      setViewingBoard(parseFen(INITIAL_FEN));
    } else {
      setViewingBoard(parseFen(history[index].fen));
    }
  }

  const isSpectator = !session?.token;

  function sendMove(from, to, promotion = null) {
    if (!wsRef.current || isSpectator) return;
    wsRef.current.send(JSON.stringify({ from_pos: from, to_pos: to, promotion }));
  }

  function sendAction(action) {
    if (!wsRef.current || isSpectator) return;
    wsRef.current.send(JSON.stringify({ action }));
  }

  function handlePromotion(pieceType) {
    const { from, to } = promotionPending;
    setPromotionPending(null);
    sendMove(from, to, pieceType);
  }

  function handleClick(row, col) {
    if (dragState.current) return;  // ignorar clicks que son sueltas de drag
    if (viewingIndex !== null) return;
    if (promotionPending) return;
    if (isSpectator) return;
    if (selectedPiece === null) {
      const piece = getPieceAt(row, col);
      if (piece) setSelectedPiece([row, col]);
    } else {
      const clickedPiece = getPieceAt(row, col);
      const selectedPieceObj = getPieceAt(selectedPiece[0], selectedPiece[1]);
      if (clickedPiece && clickedPiece.color === selectedPieceObj?.color) {
        setSelectedPiece([row, col]);
        return;
      }
      const isPromotion = selectedPieceObj?.type === 'pawn' &&
        ((selectedPieceObj.color === 'white' && row === 7) ||
         (selectedPieceObj.color === 'black' && row === 0));
      if (isPromotion) {
        setPromotionPending({ from: selectedPiece, to: [row, col], color: selectedPieceObj.color });
        setSelectedPiece(null);
        return;
      }
      sendMove(selectedPiece, [row, col]);
    }
  }

  const isDraggingFrom = dragState.current?.from;

  if (!session) return <Lobby onJoin={setSession} />;

  return (
    <div style={{ display: 'flex', gap: '20px', userSelect: 'none' }}>
      {/* Pieza flotante que sigue el cursor durante el drag */}
      {dragPos && dragState.current && (
        <img
          src={getPieceImage(dragState.current.piece)}
          alt="dragging"
          width={60}
          height={60}
          style={{
            position: 'fixed',
            left: dragPos.x - 30,
            top: dragPos.y - 30,
            pointerEvents: 'none',
            zIndex: 1000,
          }}
        />
      )}

      <div>
        <h1>Chess Engine</h1>
        <button onClick={() => setFlipped(!flipped)}>Rotar tablero</button>
        {!isSpectator && !gameOver && (
          <>
            <button onClick={() => sendAction('offer_draw')} disabled={!!drawOffer}>
              Ofrecer tablas
            </button>
            <button onClick={() => { if (window.confirm('¿Seguro que querés rendirte?')) sendAction('resign'); }}>
              Rendirse
            </button>
          </>
        )}
        {isSpectator && <span style={{ fontSize: 13, color: '#888' }}>👁 Modo espectador</span>}
        {roomData && (
          <div style={{ marginBottom: 6, display: 'flex', justifyContent: 'space-between', fontWeight: 'bold' }}>
            <span>{flipped ? (roomData.player_white || 'Esperando blancas...') : (roomData.player_black || 'Esperando negras...')}</span>
            <span>{flipped ? formatTime(timeWhite) : formatTime(timeBlack)}</span>
          </div>
        )}
        <div style={{ position: 'relative', display: 'inline-block' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 60px)' }}>
            {rows.flatMap(row =>
              cols.map(col => {
                const piece = getPieceAt(row, col);
                const isLight = (row + col) % 2 === 0;
                const isKingInCheck = piece && piece.type === 'king' &&
                  ((piece.color === 'white' && whiteInCheck) || (piece.color === 'black' && blackInCheck));
                const isBeingDragged = isDraggingFrom &&
                  isDraggingFrom[0] === row && isDraggingFrom[1] === col;
                return (
                  <div
                    key={`${row}-${col}`}
                    data-square={`${row},${col}`}
                    onClick={() => handleClick(row, col)}
                    style={{
                      width: 60,
                      height: 60,
                      backgroundColor: isKingInCheck ? '#ff0000' : (isLight ? '#f0d9b5' : '#b58863'),
                    }}
                  >
                    {piece && (
                      <img
                        src={getPieceImage(piece)}
                        alt={piece.type}
                        width={60}
                        height={60}
                        draggable={false}
                        onMouseDown={(e) => {
                          if (viewingIndex !== null || promotionPending || isSpectator) return;
                          e.preventDefault();
                          dragState.current = { piece, from: [row, col] };
                          setDragPos({ x: e.clientX, y: e.clientY });
                          setSelectedPiece(null);
                        }}
                        style={{
                          cursor: 'grab',
                          display: 'block',
                          opacity: isBeingDragged ? 0 : 1,
                        }}
                      />
                    )}
                  </div>
                );
              })
            )}
          </div>
          {drawOffer && drawOffer !== session?.color && (
            <div style={{
              position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.5)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              zIndex: 20,
            }}>
              <div style={{
                backgroundColor: 'white', borderRadius: '10px', padding: '28px 36px',
                display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px',
                boxShadow: '0 6px 30px rgba(0,0,0,0.4)',
              }}>
                <span style={{ fontWeight: 'bold', fontSize: '16px' }}>Te ofrecen tablas</span>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button onClick={() => { sendAction('accept_draw'); setDrawOffer(null); }}
                    style={{ padding: '8px 20px', background: '#769656', color: 'white', border: 'none', borderRadius: 6, cursor: 'pointer', fontWeight: 'bold' }}>
                    Aceptar
                  </button>
                  <button onClick={() => { sendAction('reject_draw'); setDrawOffer(null); }}
                    style={{ padding: '8px 20px', border: '1px solid #ccc', borderRadius: 6, cursor: 'pointer' }}>
                    Rechazar
                  </button>
                </div>
              </div>
            </div>
          )}
          {gameOver && (
            <div style={{
              position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              zIndex: 20,
            }}>
              <div style={{
                backgroundColor: 'white',
                borderRadius: '10px',
                padding: '32px 40px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '16px',
                boxShadow: '0 6px 30px rgba(0,0,0,0.5)',
                textAlign: 'center',
              }}>
                <span style={{ fontSize: '22px', fontWeight: 'bold' }}>
                  {gameOver.result === 'white_wins' ? 'Ganan las blancas' :
                   gameOver.result === 'black_wins' ? 'Ganan las negras' : '½ - ½ Tablas'}
                </span>
                <span style={{ fontSize: '14px', color: '#666' }}>
                  {gameOver.reason === 'timeout' ? 'Tiempo agotado' :
                   gameOver.reason === 'checkmate' ? 'Jaque mate' :
                   gameOver.reason === 'resign' ? 'Abandono' : 'Tablas por acuerdo'}
                </span>
              </div>
            </div>
          )}
          {promotionPending && (
            <div style={{
              position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.5)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              zIndex: 10,
            }}>
              <div style={{
                backgroundColor: 'white',
                borderRadius: '8px',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '12px',
                boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
              }}>
                <span style={{ fontWeight: 'bold', fontSize: '16px' }}>Elegir pieza</span>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {['queen', 'rook', 'bishop', 'knight'].map(pieceType => (
                    <div key={pieceType} onClick={() => handlePromotion(pieceType)} style={{
                      cursor: 'pointer',
                      width: 60, height: 60,
                      border: '2px solid #ccc',
                      borderRadius: '6px',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}
                      onMouseEnter={e => e.currentTarget.style.borderColor = '#769656'}
                      onMouseLeave={e => e.currentTarget.style.borderColor = '#ccc'}
                    >
                      <img src={getPieceImage({ color: promotionPending.color, type: pieceType })} width={52} height={52} alt={pieceType} />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
        {roomData && (
          <div style={{ marginTop: 6, display: 'flex', justifyContent: 'space-between', fontWeight: 'bold' }}>
            <span>{flipped ? (roomData.player_black || 'Esperando negras...') : (roomData.player_white || 'Esperando blancas...')}</span>
            <span>{flipped ? formatTime(timeBlack) : formatTime(timeWhite)}</span>
          </div>
        )}
      </div>
      <div style={{ width: '200px' }}>
        <h3>Movimientos</h3>
        <div style={{ overflowY: 'auto', maxHeight: '400px' }}>
          {history.reduce((pairs, move, index) => {
            if (index % 2 === 0) pairs.push([move]);
            else pairs[pairs.length - 1].push(move);
            return pairs;
          }, []).map((pair, index) => (
            <div key={index} style={{ padding: '4px' }}>
              {index + 1}.{' '}
              <span onClick={() => goToPosition(index * 2)} style={{
                cursor: 'pointer',
                backgroundColor: (viewingIndex === index * 2 || (viewingIndex === null && index * 2 === history.length - 1)) ? '#769656' : 'transparent',
                color: (viewingIndex === index * 2 || (viewingIndex === null && index * 2 === history.length - 1)) ? 'white' : 'inherit',
                padding: '2px 4px',
                borderRadius: '3px'
              }}>
                {pair[0].san}
              </span>
              {pair[1] && (
                <span onClick={() => goToPosition(index * 2 + 1)} style={{
                  cursor: 'pointer',
                  backgroundColor: (viewingIndex === index * 2 + 1 || (viewingIndex === null && index * 2 + 1 === history.length - 1)) ? '#769656' : 'transparent',
                  color: (viewingIndex === index * 2 + 1 || (viewingIndex === null && index * 2 + 1 === history.length - 1)) ? 'white' : 'inherit',
                  padding: '2px 4px',
                  borderRadius: '3px'
                }}>
                  {' '}{pair[1].san}
                </span>
              )}
            </div>
          ))}
          <div ref={historyEndRef} />
        </div>
        <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
          <button onClick={() => goToPosition(-1)}>⏮</button>
          <button onClick={() => {
            if (viewingIndex === null) goToPosition(history.length - 2);
            else if (viewingIndex > -1) goToPosition(viewingIndex - 1);
          }}>◀</button>
          <button onClick={() => {
            if (viewingIndex === null) return;
            const next = viewingIndex + 1;
            if (next < history.length) goToPosition(next);
            else goToPosition(null);
          }}>▶</button>
          <button onClick={() => goToPosition(null)}>⏭</button>
        </div>
      </div>
    </div>
  );
}

export default App;
