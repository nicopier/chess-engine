import { useState } from 'react';

const API = 'http://localhost:8000';

export default function Lobby({ onJoin }) {
  const [screen, setScreen] = useState('home'); // 'home' | 'guest' | 'room'
  const [nickname, setNickname] = useState('');
  const [mode, setMode] = useState(null); // 'create' | 'join'
  const [roomId, setRoomId] = useState('');
  const [color, setColor] = useState('white');
  const [error, setError] = useState(null);

  async function handleCreate() {
    setError(null);
    const res = await fetch(`${API}/rooms`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: roomId }),
    });
    if (!res.ok) {
      const data = await res.json();
      setError(data.detail);
      return;
    }
    await joinRoom();
  }

  async function joinRoom() {
    setError(null);
    const res = await fetch(`${API}/rooms/${roomId}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: nickname, color }),
    });
    const data = await res.json();
    if (!res.ok) {
      setError(data.detail);
      return;
    }
    onJoin({ roomId, playerId: nickname, color });
  }

  if (screen === 'home') {
    return (
      <div style={styles.center}>
        <h1>Chess Engine</h1>
        <div style={styles.col}>
          <button style={styles.btn} onClick={() => setScreen('guest')}>Entrar como invitado</button>
          <button style={{ ...styles.btn, opacity: 0.5, cursor: 'not-allowed' }} disabled>Crear cuenta (próximamente)</button>
        </div>
      </div>
    );
  }

  if (screen === 'guest' && !mode) {
    return (
      <div style={styles.center}>
        <h2>Entrar como invitado</h2>
        <div style={styles.col}>
          <input
            style={styles.input}
            placeholder="Nickname"
            value={nickname}
            onChange={e => setNickname(e.target.value)}
          />
          <div style={{ display: 'flex', gap: 8 }}>
            <button style={styles.btn} onClick={() => setMode('create')} disabled={!nickname}>Crear sala</button>
            <button style={styles.btn} onClick={() => setMode('join')} disabled={!nickname}>Unirse a sala</button>
          </div>
          <button onClick={() => setScreen('home')}>Volver</button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.center}>
      <h2>{mode === 'create' ? 'Crear sala' : 'Unirse a sala'}</h2>
      <div style={styles.col}>
        <input
          style={styles.input}
          placeholder="Código de sala"
          value={roomId}
          onChange={e => setRoomId(e.target.value)}
        />
        <select style={styles.input} value={color} onChange={e => setColor(e.target.value)}>
          <option value="white">Blancas</option>
          <option value="black">Negras</option>
        </select>

        {error && <span style={{ color: 'red' }}>{error}</span>}

        <div style={{ display: 'flex', gap: 8 }}>
          <button style={styles.btn} onClick={mode === 'create' ? handleCreate : joinRoom} disabled={!roomId}>
            {mode === 'create' ? 'Crear y unirse' : 'Unirse'}
          </button>
          <button onClick={() => { setMode(null); setError(null); }}>Volver</button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  center: { display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: 80, gap: 24 },
  col: { display: 'flex', flexDirection: 'column', gap: 12, minWidth: 260 },
  btn: { padding: '8px 16px', cursor: 'pointer' },
  input: { padding: '8px', fontSize: 14 },
};
