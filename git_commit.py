import subprocess
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

os.chdir(r'C:\Users\user\Documents\cursor\weather2')

# Git add
subprocess.run(['git', 'add', '.'], check=True)
print("✓ 파일 스테이징 완료")

# Git commit
commit_message = """추가 기능 구현: 다크모드, 주간 날씨, 이메일 알림, 복장 DB, 일출시간

새로운 기능:
- 다크모드 지원 (localStorage 기반 테마 전환)
- 주간 날씨 예보 (7일간 새벽 날씨)
- 이메일 알림 설정 (User 모델에 email 필드 추가)
- 복장 추천 데이터베이스 모델 (OutfitRecommendation)
- 일출/일몰 시간 계산 기능

업데이트 파일:
- models.py: User 모델 이메일 필드 추가, OutfitRecommendation 모델 추가
- weather_service.py: 주간 날씨 조회, 일출 시간 계산 함수
- app.py: 주간 날씨 라우트 추가
- static/css/style.css: 다크모드 CSS 변수 및 토글 버튼
- static/js/main.js: 다크모드 토글 JavaScript
- templates/base.html: 주간 날씨 메뉴, 다크모드 토글 버튼
- templates/weekly.html: 주간 날씨 페이지 (신규)
- requirements.txt: Flask-Mail, suntime 추가

향후 업데이트:
- 사용자별 복장 추천 커스터마이징
- 이메일 전송 기능 완성
- 일출시간 UI 표시
"""

subprocess.run(['git', 'commit', '-m', commit_message], check=True)
print("✓ 커밋 완료")

# Git log 확인
print("\nGit 로그:")
subprocess.run(['git', 'log', '--oneline', '-5'])
