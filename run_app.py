import sys
import os

# UTF-8 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 현재 디렉토리 설정
os.chdir(r'C:\Users\user\Documents\cursor\weatherccc')

# Flask 앱 실행
from app import app
from scheduler import init_scheduler

# 스케줄러 초기화
scheduler = init_scheduler(app)

try:
    print("\n" + "="*50)
    print("새벽런닝 기상정보 웹 애플리케이션 시작")
    print("="*50)
    print(f"\n브라우저에서 접속하세요: http://localhost:5000")
    print(f"또는: http://127.0.0.1:5000")
    print("\n종료하려면 Ctrl+C를 누르세요\n")
    print("="*50 + "\n")

    app.run(debug=False, host='127.0.0.1', port=5000, threaded=True, use_reloader=False)
except KeyboardInterrupt:
    scheduler.shutdown()
    print('\n\n앱이 종료되었습니다.')
except Exception as e:
    print(f'\n오류 발생: {e}')
    import traceback
    traceback.print_exc()
    scheduler.shutdown()
