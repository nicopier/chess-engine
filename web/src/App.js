import { useState, useEffect } from 'react';

function App() {
  const[board, setBoard] = useState([]);
  const [selectedPiece, setSelectedPiece] = useState(null);
  const [whiteInCheck, setWhiteInCheck] = useState(false);
  const [blackInCheck, setBlackInCheck] = useState(false);
  const [flipped, setFlipped] = useState(false);
  const rows = flipped ? [0,1,2,3,4,5,6,7] : [7,6,5,4,3,2,1,0];
  const cols = flipped ? [7,6,5,4,3,2,1,0] : [0,1,2,3,4,5,6,7];
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

  function handleClick(row, col) {
  if (selectedPiece === null) {
    const piece = getPieceAt(row, col);
    if (piece) setSelectedPiece([row, col]);
  } else {
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
      }
      setSelectedPiece(null);
    });
  }
}
  return (
    <div>
      <h1>Chess Engine</h1>
      <button onClick={() => setFlipped(!flipped)}>Rotar tablero</button>
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
  );

}

export default App;