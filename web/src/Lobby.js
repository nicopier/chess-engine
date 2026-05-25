import { useState, useEffect } from 'react';

const API = process.env.REACT_APP_API_URL;

function formatTime(secs) {
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return s === 0 ? `${m} min` : `${m}:${String(s).padStart(2, '0')}`;
}

export default function Lobby({ onJoin }) {
  const [nickname, setNickname] = useState('');
  const [nicknameSet, setNicknameSet] = useState(false);
  const [rooms, setRooms] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [comment, setComment] = useState('');
  const [timeControl, setTimeControl] = useState(600);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!nicknameSet) return;
    fetchRooms();
    const interval = setInterval(fetchRooms, 3000);
    return () => clearInterval(interval);
  }, [nicknameSet]);

  async function fetchRooms() {
    const res = await fetch(`${API}/rooms`);
    const data = await res.json();
    setRooms(data);
  }

  async function handleCreate() {
    setError(null);
    const res = await fetch(`${API}/rooms`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ creator: nickname, comment, time_control: timeControl }),
    });
    const data = await res.json();
    if (!res.ok) { setError(data.detail); return; }
    await joinRoom(data.id, 'white');
  }

  async function joinRoom(roomId, color) {
    setError(null);
    const res = await fetch(`${API}/rooms/${roomId}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: nickname, color }),
    });
    const data = await res.json();
    if (!res.ok) { setError(data.detail); return; }
    onJoin({ roomId, playerId: nickname, color, token: data.token });
  }

  function watchRoom(roomId) {
    onJoin({ roomId, playerId: null, color: null });
  }

  function availableColors(room) {
    const colors = [];
    if (!room.player_white) colors.push('white');
    if (!room.player_black) colors.push('black');
    return colors;
  }

  if (!nicknameSet) {
    return (
      <div style={styles.center}>
        <h1>Chess Engine</h1>
        <div style={styles.col}>
          <input
            style={styles.input}
            placeholder="Nickname"
            value={nickname}
            onChange={e => setNickname(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && nickname && setNicknameSet(true)}
          />
          <button style={styles.btn} onClick={() => setNicknameSet(true)} disabled={!nickname}>
            Entrar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <h2 style={{ margin: 0 }}>Partidas disponibles</h2>
        <button style={styles.btnGreen} onClick={() => setShowCreate(true)}>+ Crear partida</button>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      {showCreate && (
        <div style={styles.overlay}>
          <div style={styles.modal}>
            <h3 style={{ marginTop: 0 }}>Crear partida</h3>
            <label style={styles.label}>Comentario (opcional)</label>
            <input
              style={styles.input}
              placeholder="ej: casual, bienvenidos todos"
              value={comment}
              onChange={e => setComment(e.target.value)}
            />
            <label style={styles.label}>Control de tiempo</label>
            <select style={styles.input} value={timeControl} onChange={e => setTimeControl(Number(e.target.value))}>
              <option value={60}>1 min</option>
              <option value={180}>3 min</option>
              <option value={300}>5 min</option>
              <option value={600}>10 min</option>
              <option value={900}>15 min</option>
              <option value={1800}>30 min</option>
            </select>
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <button style={styles.btnGreen} onClick={handleCreate}>Crear</button>
              <button onClick={() => { setShowCreate(false); setError(null); }}>Cancelar</button>
            </div>
          </div>
        </div>
      )}

      <div style={styles.list}>
        {rooms.length === 0 && (
          <div style={styles.empty}>No hay partidas disponibles. ¡Creá una!</div>
        )}
        {rooms.map(room => {
          const colors = availableColors(room);
          const isPlaying = room.status === 'playing';
          return (
            <div key={room.id} style={styles.card}>
              <div style={styles.cardLeft}>
                <div style={styles.cardTitle}>{room.creator}</div>
                {room.comment && <div style={styles.cardComment}>{room.comment}</div>}
                <div style={styles.cardMeta}>
                  {formatTime(room.time_control)} · {isPlaying ? '⚔️ Jugando' : '⏳ Esperando'}
                </div>
              </div>
              <div style={styles.cardActions}>
                {!isPlaying && colors.includes('white') && (
                  <button style={styles.btnSmall} onClick={() => joinRoom(room.id, 'white')}>Blancas</button>
                )}
                {!isPlaying && colors.includes('black') && (
                  <button style={styles.btnSmall} onClick={() => joinRoom(room.id, 'black')}>Negras</button>
                )}
                <button style={{ ...styles.btnSmall, background: '#888' }} onClick={() => watchRoom(room.id)}>
                  👁 Ver
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

const styles = {
  page: { maxWidth: 640, margin: '40px auto', padding: '0 16px', fontFamily: 'sans-serif' },
  center: { display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: 120, gap: 24, fontFamily: 'sans-serif' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  col: { display: 'flex', flexDirection: 'column', gap: 12, minWidth: 260 },
  list: { display: 'flex', flexDirection: 'column', gap: 12 },
  card: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid #ddd', borderRadius: 8, padding: '14px 16px', background: '#fff' },
  cardLeft: { display: 'flex', flexDirection: 'column', gap: 4 },
  cardTitle: { fontWeight: 'bold', fontSize: 15 },
  cardComment: { fontSize: 13, color: '#555' },
  cardMeta: { fontSize: 12, color: '#888' },
  cardActions: { display: 'flex', gap: 8 },
  btn: { padding: '8px 16px', cursor: 'pointer', borderRadius: 6, border: '1px solid #ccc' },
  btnGreen: { padding: '8px 16px', cursor: 'pointer', borderRadius: 6, border: 'none', background: '#769656', color: 'white', fontWeight: 'bold' },
  btnSmall: { padding: '6px 12px', cursor: 'pointer', borderRadius: 6, border: 'none', background: '#769656', color: 'white', fontSize: 13 },
  input: { padding: '8px', fontSize: 14, borderRadius: 6, border: '1px solid #ccc' },
  label: { fontSize: 13, color: '#555', marginBottom: 2 },
  error: { color: 'red', marginBottom: 12 },
  empty: { color: '#aaa', textAlign: 'center', padding: 40 },
  overlay: { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 },
  modal: { background: 'white', borderRadius: 10, padding: 28, display: 'flex', flexDirection: 'column', gap: 10, minWidth: 320, boxShadow: '0 4px 20px rgba(0,0,0,0.3)' },
};
