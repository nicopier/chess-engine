import { useState, useEffect } from 'react';

function App() {
  const[board, setBoard] = useState([]);
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

  return (
    <div>
      <h1>Chess Engine</h1>
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(8, 60px)'}}>
        {[7,6,5,4,3,2,1,0].flatMap(row =>
          [0,1,2,3,4,5,6,7].map(col => {
            const piece = getPieceAt(row, col);
            const isLight = (row + col) % 2 === 0;
            return (
              <div key={`${row}-${col}`} style={{
                width: 60,
                height: 60,
                backgroundColor: isLight ? '#f0d9b5' : '#b58863',
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