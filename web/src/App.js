import { useState, useEffect, useRef } from 'react';

function App() {
  const historyEndRef = useRef(null);
  const[board, setBoard] = useState([]);
  const [selectedPiece, setSelectedPiece] = useState(null);
  const [whiteInCheck, setWhiteInCheck] = useState(false);
  const [blackInCheck, setBlackInCheck] = useState(false);
  const [flipped, setFlipped] = useState(false);
  const rows = flipped ? [0,1,2,3,4,5,6,7] : [7,6,5,4,3,2,1,0];
  const cols = flipped ? [7,6,5,4,3,2,1,0] : [0,1,2,3,4,5,6,7];
  const INITIAL_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w';
  const [history, setHistory] = useState([]);
  const [viewingIndex, setViewingIndex] = useState(null);
  const [viewingBoard, setViewingBoard] = useState(null);
  

  useEffect(() => {
    fetch('http://localhost:8000/board')
    .then(response => response.json())
    .then(data => setBoard(data))
  }, []);

  useEffect(() => {
    if (historyEndRef.current) {
      historyEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [history]);
  
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
  const currentBoard = viewingBoard ?? board;
  return currentBoard.find(p => p.position[0] === row && p.position[1] === col);
}
  function parseFen(fen) {
    const fenToType = {
      'p': 'pawn', 'r': 'rook', 'n': 'knight',
      'b': 'bishop', 'q': 'queen', 'k': 'king'
    };
    const pieces = [];
    const rows = fen.split(' ')[0].split('/');
    rows.forEach((row, rowIndex) => {
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
        setViewingBoard(null);
        setViewingIndex(null);
      });
  }

 function goToPosition(index) {
  if (index === history.length - 1) {
    setViewingIndex(null);
    setViewingBoard(null);
    fetch('http://localhost:8000/goto/last', { method: 'POST' });
    return;
    }
    setViewingIndex(index);
    if (index === null) {
      setViewingBoard(null);
      fetch('http://localhost:8000/goto/last', { method: 'POST' });
    } else if (index === -1) {
      setViewingBoard(parseFen(INITIAL_FEN));
      fetch('http://localhost:8000/goto/0', { method: 'POST' });
    } else {
      setViewingBoard(parseFen(history[index].fen));
    }
  }

  function handleClick(row, col) {
    if (viewingIndex !== null) return;
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
          setViewingBoard(null);
          setViewingIndex(null);
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
    <div style={{width: '200px'}}>
      <h3>Movimientos</h3>
      <div style={{overflowY: 'auto', maxHeight: '400px'}}>
        {history.reduce((pairs, move, index) => {
          if (index % 2 === 0) pairs.push([move]);
          else pairs[pairs.length - 1].push(move);
          return pairs;
          
        }, []).map((pair, index) => (
          <div key={index} style={{padding: '4px'}}>
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
      <div style={{display: 'flex', gap: '8px', marginTop: '10px'}}>
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