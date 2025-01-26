import random
import copy
import json

class ChessSudokuBoard:
    def __init__(self):
        # 9x9 보드 초기화
        self.board = [[None for _ in range(9)] for _ in range(9)]

        self.pieces = {
            'king': '♚',
            'bishop': '♝',
            'knight': '♞',
            'rook': '♜'
        }

        # 각 기물의 위치 저장
        self.piece_positions = {
            'king': [],
            'bishop': [],
            'knight': [],
            'rook': []
        }

        # 나이트의 이동 위치에 있는 숫자들을 추적하기 위한 딕셔너리
        self.knight_move_numbers = {}
        # 비숍의 대각선 위치에 있는 숫자들을 추적하기 위한 딕셔너리
        self.bishop_diagonals = {}
        # 킹 주변의 숫자들을 추적하기 위한 딕셔너리
        self.king_adjacent_numbers = {}

    def to_dict(self):
        """보드 상태를 딕셔너리로 변환"""
        return {
            'board': [
                [cell if isinstance(cell, (int, type(None))) else str(cell) 
                 for cell in row]
                for row in self.board
            ],
            'piece_positions': self.piece_positions,
            'knight_move_numbers': {
                f"{pos[0]},{pos[1]}": list(numbers) 
                for pos, numbers in self.knight_move_numbers.items()
            },
            'bishop_diagonals': {
                f"{pos[0]},{pos[1]}": {
                    'main': list(diags['main']),
                    'anti': list(diags['anti'])
                }
                for pos, diags in self.bishop_diagonals.items()
            },
            'king_adjacent_numbers': {
                f"{pos[0]},{pos[1]}": list(numbers)
                for pos, numbers in self.king_adjacent_numbers.items()
            }
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 보드 상태 복원"""
        board = cls()
        
        # 보드 상태 복원
        for i in range(9):
            for j in range(9):
                cell = data['board'][i][j]
                if isinstance(cell, str) and cell in board.pieces.values():
                    piece_type = next(k for k, v in board.pieces.items() if v == cell)
                    board.place_piece(piece_type, i, j)
                else:
                    board.board[i][j] = cell if cell != 'None' else None

        # 숫자 추적 데이터 복원
        for pos_str, numbers in data['knight_move_numbers'].items():
            i, j = map(int, pos_str.split(','))
            board.knight_move_numbers[(i, j)] = set(numbers)

        for pos_str, diags in data['bishop_diagonals'].items():
            i, j = map(int, pos_str.split(','))
            board.bishop_diagonals[(i, j)] = {
                'main': set(diags['main']),
                'anti': set(diags['anti'])
            }

        for pos_str, numbers in data['king_adjacent_numbers'].items():
            i, j = map(int, pos_str.split(','))
            board.king_adjacent_numbers[(i, j)] = set(numbers)

        return board

    def to_json(self):
        """보드 상태를 JSON 문자열로 변환"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str):
        """JSON 문자열에서 보드 상태 복원"""
        return cls.from_dict(json.loads(json_str))

    def get_king_moves(self, row, col):
        """킹의 이동 가능한 위치(주변 8방향) 반환"""
        moves = [
            (row-1, col-1), (row-1, col), (row-1, col+1),
            (row, col-1),                 (row, col+1),
            (row+1, col-1), (row+1, col), (row+1, col+1)
        ]
        return [(r, c) for r, c in moves if 0 <= r < 9 and 0 <= c < 9]

    def get_bishop_diagonals(self, row, col):
        """비숍의 대각선 이동 가능한 위치들을 반환"""
        diagonals = {
            'main': [],    # 왼쪽 위에서 오른쪽 아래 방향
            'anti': []     # 오른쪽 위에서 왼쪽 아래 방향
        }
        
        # 메인 대각선 (↘️)
        r, c = row - 1, col - 1
        while r >= 0 and c >= 0:
            if not isinstance(self.board[r][c], str):  # 체스 기물이 없는 경우만
                diagonals['main'].append((r, c))
            else:
                break  # 체스 기물을 만나면 그 방향으로의 탐색 중단
            r, c = r - 1, c - 1

        r, c = row + 1, col + 1
        while r < 9 and c < 9:
            if not isinstance(self.board[r][c], str):
                diagonals['main'].append((r, c))
            else:
                break
            r, c = r + 1, c + 1

        # 반대 대각선 (↙️)
        r, c = row - 1, col + 1
        while r >= 0 and c < 9:
            if not isinstance(self.board[r][c], str):
                diagonals['anti'].append((r, c))
            else:
                break
            r, c = r - 1, c + 1

        r, c = row + 1, col - 1
        while r < 9 and c >= 0:
            if not isinstance(self.board[r][c], str):
                diagonals['anti'].append((r, c))
            else:
                break
            r, c = r + 1, c - 1

        return diagonals

    def get_knight_moves(self, row, col):
        """나이트의 이동 가능한 위치 반환"""
        moves = [
            (row-2, col-1), (row-2, col+1),
            (row-1, col-2), (row-1, col+2),
            (row+1, col-2), (row+1, col+2),
            (row+2, col-1), (row+2, col+1)
        ]
        return [(r, c) for r, c in moves if 0 <= r < 9 and 0 <= c < 9]

    def mark_piece_moves(self, piece, row, col):
        """체스 기물이 이동 가능한 위치에 표시"""
        moves = []
        if piece == 'knight':
            moves = self.get_knight_moves(row, col)
            mark = 'N'            
        for r, c in moves:
            if self.board[r][c] is None:  # 빈 칸일 경우에만 표시
                self.board[r][c] = mark

    def place_piece(self, piece, row, col):
        """체스 기물을 보드에 배치하고 이동 가능 위치 표시"""
        if piece in self.pieces and 0 <= row < 9 and 0 <= col < 9:
            self.board[row][col] = self.pieces[piece]
            self.piece_positions[piece].append((row, col))
            
            if piece == 'knight':
                self.knight_move_numbers[(row, col)] = set()

            elif piece == 'bishop':
                self.bishop_diagonals[(row, col)] = {
                    'main': set(),
                    'anti': set()
                }
            elif piece == 'king':
                self.king_adjacent_numbers[(row, col)] = set()
            return True
        return False

    def is_valid_number(self, row, col, num):
        """주어진 위치에 숫자를 놓을 수 있는지 확인"""
        # 체스 기물이 있는 칸인지 확인
        if isinstance(self.board[row][col], str) and self.board[row][col] in self.pieces.values():
            return False
            
        # 행 검사
        for j in range(9):
            if self.board[row][j] == num:
                return False
                
        # 열 검사
        for i in range(9):
            if self.board[i][col] == num:
                return False
                
        # 3x3 박스 검사
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] == num:
                    return False
        
        # 나이트 이동 규칙 검사
        for knight_pos in self.piece_positions['knight']:
            knight_moves = self.get_knight_moves(*knight_pos)
            if (row, col) in knight_moves:
                if num in self.knight_move_numbers[knight_pos]:
                    return False
    
        # 비숍 대각선 규칙 검사
        for bishop_pos in self.piece_positions['bishop']:
            diagonals = self.get_bishop_diagonals(*bishop_pos)
            
            # 메인 대각선 검사
            if (row, col) in diagonals['main']:
                if num in self.bishop_diagonals[bishop_pos]['main']:
                    return False
            
            # 반대 대각선 검사
            if (row, col) in diagonals['anti']:
                if num in self.bishop_diagonals[bishop_pos]['anti']:
                    return False
                
        # 킹 주변 규칙 검사
        for king_pos in self.piece_positions['king']:
            king_moves = self.get_king_moves(*king_pos)
            if (row, col) in king_moves:
                if num in self.king_adjacent_numbers[king_pos]:
                    return False
                
        return True

    def get_piece_moves(self, row, col):
        """특정 위치의 기물이 이동 가능한 모든 위치 반환"""
        piece = self.board[row][col]
        if piece == self.pieces['knight']:
            return self.get_knight_moves(row, col)
        return []

    def place_number(self, row, col, num):
        """숫자를 보드에 배치"""
        if self.is_valid_number(row, col, num):
            self.board[row][col] = num
            
            # 나이트의 이동 범위에 있는 경우 해당 숫자 기록
            for knight_pos in self.piece_positions['knight']:
                knight_moves = self.get_knight_moves(*knight_pos)
                if (row, col) in knight_moves:
                    self.knight_move_numbers[knight_pos].add(num)

            # 비숍의 대각선 범위에 있는 경우 해당 숫자 기록
            for bishop_pos in self.piece_positions['bishop']:
                diagonals = self.get_bishop_diagonals(*bishop_pos)
                if (row, col) in diagonals['main']:
                    self.bishop_diagonals[bishop_pos]['main'].add(num)
                if (row, col) in diagonals['anti']:
                    self.bishop_diagonals[bishop_pos]['anti'].add(num)

            # 킹의 주변 8방향에 있는 경우 해당 숫자 기록
            for king_pos in self.piece_positions['king']:
                king_moves = self.get_king_moves(*king_pos)
                if (row, col) in king_moves:
                    self.king_adjacent_numbers[king_pos].add(num)
            return True
        return False
    
    def print_board(self):
        """보드 출력"""

        print("┌───────────────────────┐")
        for i, row in enumerate(self.board):
            # 행 시작
            print("│", end=" ")
            
            for j, cell in enumerate(row):
                # 셀 내용 출력
                if cell is None:
                    print(".", end=" ")
                else:
                    print(cell, end=" ")
                    
                # 3x3 박스 구분선
                if j % 3 == 2 and j < 8:
                    print("│", end=" ")
                    
            # 행 끝
            print("│")
            
            # 3x3 박스 구분선
            if i % 3 == 2 and i < 8:
                print("├───────────────────────┤")
                
        # 하단 테두리
        print("└───────────────────────┘")

def find_empty_cell(board):
    """비어있는 셀(None)을 찾아 반환"""
    for i in range(9):
        for j in range(9):
            if isinstance(board.board[i][j], (int, type(None))):
                if board.board[i][j] is None:
                    return i, j
    return None

def solve_sudoku(board):
    """백트래킹을 사용하여 스도쿠 해결"""
    import random
    
    empty = find_empty_cell(board)
    
    # 모든 셀이 채워졌다면 완료
    if empty is None:
        return True
        
    row, col = empty
    
    # 1-9를 랜덤하게 섞어서 시도
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    
    for num in numbers:
        # 현재 숫자가 유효한지 확인
        if board.is_valid_number(row, col, num):
            # 숫자 배치
            board.place_number(row, col, num)
            
            # 재귀적으로 나머지 셀 해결 시도
            if solve_sudoku(board):
                return True
                
            # 해결책을 찾지 못했다면 백트래킹
            board.board[row][col] = None

            # 나이트의 이동 범위에서 숫자 제거
            for knight_pos in board.piece_positions['knight']:
                knight_moves = board.get_knight_moves(*knight_pos)
                if (row, col) in knight_moves:
                    board.knight_move_numbers[knight_pos].discard(num)

            # 비숍의 대각선에서 숫자 제거
            for bishop_pos in board.piece_positions['bishop']:
                diagonals = board.get_bishop_diagonals(*bishop_pos)
                if (row, col) in diagonals['main']:
                    board.bishop_diagonals[bishop_pos]['main'].discard(num)
                if (row, col) in diagonals['anti']:
                    board.bishop_diagonals[bishop_pos]['anti'].discard(num)
    
            # 킹의 주변에서 숫자 제거
            for king_pos in board.piece_positions['king']:
                king_moves = board.get_king_moves(*king_pos)
                if (row, col) in king_moves:
                    board.king_adjacent_numbers[king_pos].discard(num)
    return False

def create_puzzle(board, difficulty='medium'):
    """완성된 스도쿠에서 숫자를 제거하여 퍼즐 생성"""
    import random
    import copy
    
    # 난이도별 제거할 셀의 개수 (체스 기물 제외)
    difficulty_levels = {
        'easy': (35, 40),    # 41-46개의 힌트
        'medium': (45, 50),  # 31-36개의 힌트
        'hard': (55, 60)     # 21-26개의 힌트
    }
    
    if difficulty not in difficulty_levels:
        difficulty = 'medium'
        
    min_remove, max_remove = difficulty_levels[difficulty]
    cells_to_remove = random.randint(min_remove, max_remove)
    
    # 제거 가능한 셀의 위치 수집 (체스 기물이 없는 위치만)
    available_cells = []
    for i in range(9):
        for j in range(9):
            if isinstance(board.board[i][j], int):
                available_cells.append((i, j))
                
    # 퍼즐 생성을 위한 보드 복사
    puzzle_board = copy.deepcopy(board)
    removed_cells = []
    
    while cells_to_remove > 0 and available_cells:
        # 랜덤하게 셀 선택
        cell_idx = random.randrange(len(available_cells))
        row, col = available_cells.pop(cell_idx)
        
        # 현재 값 저장
        temp_value = puzzle_board.board[row][col]
        # 셀 비우기
        puzzle_board.board[row][col] = None
        
        # 유일해 체크
        temp_board = copy.deepcopy(puzzle_board)
        solution_count = count_solutions(temp_board, max_count=2)
        
        if solution_count == 1:
            # 제거 성공
            removed_cells.append((row, col, temp_value))
            cells_to_remove -= 1
        else:
            # 제거 실패 - 값 복구
            puzzle_board.board[row][col] = temp_value
            
    return puzzle_board, removed_cells

def count_solutions(board, max_count=1):
    """주어진 보드의 해답 개수를 세는 함수 (max_count까지만)"""
    solutions = [0]
    
    def solve_counter(b):
        if solutions[0] >= max_count:
            return
            
        empty = find_empty_cell(b)
        if empty is None:
            solutions[0] += 1
            return
            
        row, col = empty
        for num in range(1, 10):
            if b.is_valid_number(row, col, num):
                b.place_number(row, col, num)
                solve_counter(b)
                b.board[row][col] = None

                # 나이트의 이동 범위에서 숫자 제거
                for knight_pos in b.piece_positions['knight']:
                    knight_moves = b.get_knight_moves(*knight_pos)
                    if (row, col) in knight_moves:
                        b.knight_move_numbers[knight_pos].discard(num)
    
                # 비숍의 대각선에서 숫자 제거
                for bishop_pos in b.piece_positions['bishop']:
                    diagonals = b.get_bishop_diagonals(*bishop_pos)
                    if (row, col) in diagonals['main']:
                        b.bishop_diagonals[bishop_pos]['main'].discard(num)
                    if (row, col) in diagonals['anti']:
                        b.bishop_diagonals[bishop_pos]['anti'].discard(num)

                # 킹의 주변에서 숫자 제거
                for king_pos in b.piece_positions['king']:
                    king_moves = b.get_king_moves(*king_pos)
                    if (row, col) in king_moves:
                        b.king_adjacent_numbers[king_pos].discard(num)
    solve_counter(board)
    return solutions[0]

def generate_puzzle(*, difficulty='medium', piece_config=None):
    """체스 스도쿠 퍼즐 생성 함수"""
    board = ChessSudokuBoard()
    
    # 기본 체스 기물 배치 설정
    default_pieces = [
        ('knight', 0, 2),
        ('knight', 4, 7),
        ('king', 7, 5),
        ('bishop', 3, 3)
    ]
    
    # piece_config가 제공된 경우 사용
    pieces_to_place = piece_config if piece_config else default_pieces
    
    # 체스 기물 배치
    for piece in pieces_to_place:
        if isinstance(piece, tuple):
            piece_type, row, col = piece
        else:
            piece_type = piece['type']
            row, col = piece['position']
        board.place_piece(piece_type, row, col)
    
    # 스도쿠 해결
    if not solve_sudoku(board):
        raise ValueError("Failed to generate valid solution")
        
    # 퍼즐 생성
    puzzle, removed = create_puzzle(board, difficulty)
    
    return {
        'puzzle': puzzle,
        'solution': board,
        'removed_cells': removed
    }


def test_puzzle_generation():
    board = ChessSudokuBoard()
    
    board.place_piece('knight', 0, 2)
    board.place_piece('knight', 4, 7)
    board.place_piece('king', 7, 5)
    board.place_piece('bishop', 3, 3)

    print("Generating complete solution:")
    if solve_sudoku(board):
        board.print_board()
        
        print("\nGenerating puzzle:")
        puzzle, removed = create_puzzle(board, 'easy')
        puzzle.print_board()
        
        print(f"\nRemoved {len(removed)} cells")
        
        # 정답 확인
        print("\nVerifying unique solution...")
        solutions = count_solutions(puzzle)
        print(f"Number of solutions: {solutions}")
