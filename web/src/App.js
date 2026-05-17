import { useState, useEffect } from 'react';

function App() {
  const[board, setBoard] = useState([]);
  const [selectedPiece, setSelectedPiece] = useState(null);
  const [whiteInCheck, setWhiteInCheck] = useState(false);
  const [blackInCheck, setBlackInCheck] = useState(false);
  const [flipped, setFlipped] = useState(false);
  const rows = flipped ? [0,1,2,3,4,5,6,7] : [7,6,5,4,3,2,1,0];
  const cols = flipped ? [7,6,5,4,3,2,1,0] : [0,1,2,3,4,5,6,7];
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/board')
    .then(response => response.json())
    .then(data => setBoard(data))
  }, []);

  function getPieceImage(piece){
    const colorLetter = piece.color === 'white' ? 'w' : 'b';
    const typeLetter = {
      pawn: 'P',
      knight: 'N',
      bishop: 'B',
      rook: 'R',
      queen: 'Q',
      king: 'K'
    }[piece.type];
    return `/pieces/${colorLetter}${typeLetter}.svg`;  
    }
  

  function getPieceAt(row, col) {
    return board.find(p => p.position[0] === row && p.position[1] === col);
  }

  function resetGame() {
  fetch('http://localhost:8000/reset', { method: 'POST' })
    .then(response => response.json())
    .then(() => {
      fetch('http://localhost:8000/board')
        .then(response => response.json())
        .then(data => setBoard(data));
      setHistory([]);
      setWhiteInCheck(false);
      setBlackInCheck(false);
      setSelectedPiece(null);
    });
}

  function handleClick(row, col) {
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
    // mandar movimiento a la API
    fetch('http://localhost:8000/move', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({from_pos: selectedPiece, to_pos: [row, col]})
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        setWhiteInCheck(data.white_in_check);
        setBlackInCheck(data.black_in_check);
        fetch('http://localhost:8000/board')
          .then(response => response.json())
          .then(data => setBoard(data));
        fetch('http://localhost:8000/history')
          .then(response => response.json())
          .then(data => setHistory(data));
      }
      setSelectedPiece(null);
    });
  }
}
  return (
    <div style={{display: 'flex', gap: '20px'}}>
      <div>
        <h1>Chess Engine</h1>
        <button onClick={() => setFlipped(!flipped)}>Rotar tablero</button>
        <button onClick={resetGame}>Nueva partida</button>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(8, 60px)'}}>
          {rows.flatMap(row =>
            cols.map(col => {
              const piece = getPieceAt(row, col);
              const isLight = (row + col) % 2 === 0;
              const isKingInCheck = piece && piece.type === 'king' && 
              ((piece.color === 'white' && whiteInCheck) || (piece.color === 'black' && blackInCheck));
              return (
                <div key={`${row}-${col}`} onClick={() => handleClick(row, col)} style={{
                  width: 60,
                  height: 60,
                  backgroundColor: isKingInCheck ? '#ff0000' : (isLight ? '#f0d9b5' : '#b58863'),
                }}>
                  {piece && <img src={getPieceImage(piece)} alt={piece.type} width={60} height={60} />}
                </div>
              );
            })
          )}
        </div>
      </div>
      <div style={{width: '200px', overflowY: 'auto', maxHeight: '480px'}}>
        <h3>Movimientos</h3>
        {history.reduce((pairs, move, index) => {
          if (index % 2 === 0) pairs.push([move]);
          else pairs[pairs.length - 1].push(move);
          return pairs;
        }, []).map((pair, index) => (
          <div key={index} style={{padding: '4px'}}>
            {index + 1}. {pair[0].san}
            {pair[1] && ` | ${pair[1].san}`}
          </div>
        ))}
      </div>
    </div>
  );
}
export default App;