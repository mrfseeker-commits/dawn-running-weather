"""
자동 업데이트 스케줄러
- 매일 자정: 모든 저장된 지역의 날씨 업데이트
- 3시간마다: 날씨 데이터 갱신
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from models import db, SavedLocation
from weather_service import update_weather_for_region
from datetime import datetime


def update_all_weather():
    """모든 저장된 지역의 날씨 업데이트"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 날씨 자동 업데이트 시작")
    print(f"{'='*60}")

    # 모든 unique 지역 코드 가져오기
    unique_locations = db.session.query(
        SavedLocation.region_code,
        SavedLocation.region_name
    ).distinct().all()

    total = len(unique_locations)
    success = 0
    failed = 0

    print(f"총 {total}개 지역 업데이트 예정\n")

    for idx, (region_code, region_name) in enumerate(unique_locations, 1):
        print(f"[{idx}/{total}] {region_name} (코드: {region_code})")

        try:
            weather_url = f"https://weather.naver.com/today/{region_code}"
            result = update_weather_for_region(region_code, weather_url)

            if result:
                success += 1
                print(f"✓ 성공\n")
            else:
                failed += 1
                print(f"✗ 실패 (데이터 없음)\n")

        except Exception as e:
            failed += 1
            print(f"✗ 실패: {e}\n")

    print(f"{'='*60}")
    print(f"업데이트 완료: 성공 {success}개, 실패 {failed}개")
    print(f"{'='*60}\n")


def init_scheduler(app):
    """
    스케줄러 초기화 및 시작

    Args:
        app: Flask 애플리케이션 인스턴스
    """
    scheduler = BackgroundScheduler()

    # Flask 앱 컨텍스트 내에서 작업 실행
    def job_with_context():
        with app.app_context():
            update_all_weather()

    # 1. 매일 자정에 실행 (다음날 날씨 크롤링)
    scheduler.add_job(
        func=job_with_context,
        trigger=CronTrigger(hour=0, minute=0),
        id='daily_update',
        name='매일 자정 날씨 업데이트',
        replace_existing=True
    )

    # 2. 매 10분마다 실행 (데이터 갱신)
    scheduler.add_job(
        func=job_with_context,
        trigger=CronTrigger(minute='*/10'),
        id='periodic_update',
        name='10분마다 날씨 갱신',
        replace_existing=True
    )

    # 3. 앱 시작 시 1회 실행 (선택사항)
    # scheduler.add_job(
    #     func=job_with_context,
    #     trigger='date',
    #     id='startup_update',
    #     name='시작 시 날씨 업데이트',
    #     replace_existing=True
    # )

    scheduler.start()

    print("✓ 스케줄러 시작됨")
    print("  - 매일 자정: 날씨 업데이트")
    print("  - 10분마다: 날씨 갱신\n")

    return scheduler


if __name__ == '__main__':
    # 테스트용
    from app import app

    with app.app_context():
        print("테스트: 날씨 업데이트 실행\n")
        update_all_weather()
