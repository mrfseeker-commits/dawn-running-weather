import subprocess
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

os.chdir(r'C:\Users\user\Documents\cursor\weather2')

# Git add
subprocess.run(['git', 'add', '.'], check=True)
print("✓ 파일 스테이징 완료")

# Git commit
commit_message = """일출/일몰 시간 표시 기능 완료

새로운 기능:
- 일출/일몰 시간 계산 및 표시
- suntime 라이브러리를 사용한 정확한 일출/일몰 시간 계산
- 사용자가 저장한 지역의 위도/경도 기반 계산

업데이트 파일:
- weather_service.py: get_sunrise_sunset() 함수 추가
- app.py: 대시보드 및 주간 예보에 일출/일몰 시간 통합
- templates/dashboard.html: 오늘/내일 일출/일몰 시간 표시
- templates/weekly.html: 주간 예보 테이블에 일출 시간 컬럼 추가
- requirements.txt: suntime==1.3.2 추가

기능 특징:
- 한국 표준시(KST, UTC+9) 기준 표시
- 각 지역의 위도/경도에 따른 정확한 계산
- 대시보드: 오늘/내일 일출/일몰 시간
- 주간 예보: 7일간 일출 시간 표시

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""

subprocess.run(['git', 'commit', '-m', commit_message], check=True)
print("✓ 커밋 완료")

# Git log 확인
print("\nGit 로그:")
subprocess.run(['git', 'log', '--oneline', '-5'])
