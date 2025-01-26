from flask import Flask, jsonify, request
from firebase_admin import credentials, firestore, initialize_app
import json
from chessudoku import ChessSudokuBoard, solve_sudoku, create_puzzle, generate_puzzle

# Flask 앱 초기화
app = Flask(__name__)

# Firebase 초기화
cred = credentials.Certificate(r'C:\Users\rwt12\Documents\python_projects\projects\chessudoku\chessudoku-c1699-firebase-adminsdk-fbsvc-16a948f726.json')
initialize_app(cred)
db = firestore.client()

def board_to_json(board):
    """체스 스도쿠 보드를 JSON 형식으로 변환"""
    result = {
        'board': [],
        'pieces': [],
    }

    # 보드의 숫자 데이터 변환
    for i in range(9):
        row = []
        for j in range(9):
            cell = board.board[i][j]
            if cell is None:
                row.append(0) # 빈 칸은 0으로 표시
            elif isinstance(cell, int):
                row.append(cell)
            else:  # 체스 기물인 경우
                row.append(0)
                result['pieces'].append({
                    'type': next(k for k, v in board.pieces.items() if v == cell),
                    'position': [i, j]
                })
        result['board'].append(row)
    return result

@app.route('/')
def hello():
    return 'Hello, Welcome ChesSudoku!'

@app.route('/generate', methods=['POST'])
def generate_puzzle_endpoint():
    try:
        data = request.get_json()
        difficulty = data.get('difficulty', 'medium')
        pieces = data.get('pieces', None)
        
        # pieces 데이터 형식 변환: 리스트를 튜플로 변환
        if pieces:
            formatted_pieces = []
            for piece in pieces:
                # piece가 리스트 형태로 오므로 튜플로 변환
                if isinstance(piece, list):
                    formatted_pieces.append(tuple(piece))
                elif isinstance(piece, dict):
                    pos = piece['position']
                    formatted_pieces.append((piece['type'], pos[0], pos[1]))
            pieces = formatted_pieces
        
        # 퍼즐 생성
        result = generate_puzzle(difficulty=difficulty, piece_config=pieces)
        
        # Firebase에 저장할 데이터 준비
        puzzle_data = {
            'puzzle': result['puzzle'].to_dict(),
            'solution': result['solution'].to_dict(),
            'removed_cells': result['removed_cells']
        }
        
        # # Firebase에 저장
        # doc_ref = db.collection('puzzles').document()
        # doc_ref.set({
        #     'puzzle_data': puzzle_data,
        #     'difficulty': difficulty,
        #     'created_at': firestore.SERVER_TIMESTAMP
        # })
        
        # puzzle_data['puzzle_id'] = doc_ref.id
        return jsonify(puzzle_data)
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # 서버 콘솔에 상세 에러 출력
        return jsonify({'error': str(e)}), 500

@app.route('/puzzles/<puzzle_id>', methods=['GET'])
def get_puzzle(puzzle_id):
    """저장된 퍼즐 조회"""
    try:
        doc_ref = db.collection('puzzles').document(puzzle_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({'error': 'Puzzle not found'}), 404
            
        return jsonify(doc.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)