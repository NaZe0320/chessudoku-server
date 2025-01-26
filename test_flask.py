import requests
import json
from chessudoku import ChessSudokuBoard

def test_generate_puzzle():
    # Flask 서버 URL
    url = 'http://localhost:5000/generate'
    
    # 테스트할 퍼즐 설정
    data = {
        'difficulty': 'medium',
        'pieces': [
            ('knight', 0, 2),
            ('knight', 4, 7),
            ('king', 7, 5),
            ('bishop', 3, 3)
        ]  # pieces를 튜플 리스트 형식으로 변경
    }
    
    # POST 요청 보내기
    try:
        print("Sending request with data:", json.dumps(data, indent=2))  # 요청 데이터 출력
        response = requests.post(url, json=data)
        
        print("\nResponse status:", response.status_code)  # 응답 상태 코드 출력
        print("Response headers:", dict(response.headers))  # 응답 헤더 출력
        print("Response content:", response.text)  # 응답 내용 출력
        
        # 응답 확인
        if response.status_code == 200:
            result = response.json()
            print("\nSuccessfully generated puzzle!")
            print(f"Puzzle ID: {result.get('puzzle_id')}")
            
            # 생성된 퍼즐 정보 출력
            puzzle_board = ChessSudokuBoard.from_dict(result['puzzle'])
            print("\nGenerated Puzzle:")
            puzzle_board.print_board()
            
        else:
            print(f"\nFailed to generate puzzle: {response.status_code}")
            print("Error details:", response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        raise  # 전체 에러 스택 트레이스 출력


if __name__ == '__main__':
    test_generate_puzzle()