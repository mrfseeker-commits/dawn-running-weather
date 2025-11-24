import sys
import os

# UTF-8 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 현재 디렉토리 설정
os.chdir(r'C:\Users\user\Documents\cursor\weather2')

# Flask 앱 가져오기
from app import app

# 스케줄러 비활성화 (대시보드 접속 시 자동 업데이트로 변경됨)

print("\n" + "="*60)
print("새벽런닝 기상정보 웹 애플리케이션 시작")
print("="*60)
print(f"\n브라우저에서 접속하세요:")
print(f"  → http://localhost:5555")
print(f"  → http://127.0.0.1:5555")
print(f"\n종료하려면 Ctrl+C를 누르세요")
print("="*60 + "\n")

try:
    from waitress import serve
    serve(app, host='127.0.0.1', port=5555, threads=4)
except KeyboardInterrupt:
    print('\n\n앱이 종료되었습니다.')
except Exception as e:
    print(f'\n오류 발생: {e}')
    import traceback
    traceback.print_exc()
