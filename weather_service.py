"""
날씨 크롤링 서비스
- 네이버 날씨 크롤링
- 데이터베이스에 저장
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from models import db, WeatherData
import re


# 기온별 러닝 복장 데이터베이스
RUNNING_OUTFIT_DB = [
    {"min_temp": 20, "outfit": "싱글렛, 쇼츠"},
    {"min_temp": 15, "outfit": "반팔 티셔츠, 쇼츠"},
    {"min_temp": 10, "outfit": "반팔/긴팔 티셔츠, 쇼츠/7부 타이즈"},
    {"min_temp": 5, "outfit": "긴팔 티셔츠, 레깅스, 얇은 바람막이/조끼"},
    {"min_temp": 0, "outfit": "기모 상의, 레깅스, 바람막이, 장갑, 귀마개"},
    {"min_temp": -7, "outfit": "보온 내의, 기모 상하의, 방풍 자켓, 방한 용품(모자, 장갑, 귀마개, 넥워머)"},
    {"min_temp": -99, "outfit": "실내 운동 권장 (너무 추움)"}
]


def get_running_outfit(temperature):
    """기온에 맞는 러닝 복장 추천"""
    for entry in RUNNING_OUTFIT_DB:
        if temperature >= entry["min_temp"]:
            return entry["outfit"]
    return "실내 운동 권장"


def crawl_weather(url, region_code):
    """
    네이버 날씨 크롤링 (현재 날씨 + 시간별 날씨)

    Args:
        url: 네이버 날씨 URL
        region_code: 지역 코드

    Returns:
        dict: {'hourly': 시간별 데이터 리스트, 'current': 현재 날씨 dict}
    """
    weather_data = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            print(f"크롤링 중: {url}")
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_selector('div#hourly .weather_table_wrap table', timeout=20000)

            # 1. 현재 날씨 크롤링 (페이지 상단의 큰 온도 표시)
            current_weather = page.evaluate("""
                () => {
                    try {
                        // 현재 온도 (큰 글씨)
                        const tempElem = document.querySelector('.temperature_text strong');
                        const temp = tempElem ? tempElem.textContent.replace('°', '').trim() : null;

                        // 현재 날씨 상태
                        const statusElem = document.querySelector('.weather_info .summary');
                        const status = statusElem ? statusElem.textContent.trim() : '';

                        // 강수/습도 등 (summary_inner에서)
                        const precipitation = document.querySelector('.summary_inner .rainfall');
                        const humidity = document.querySelector('.summary_inner .humidity');

                        return {
                            temperature: temp,
                            weather_status: status,
                            precipitation_prob: precipitation ? precipitation.textContent.trim() : '0',
                            humidity: humidity ? humidity.textContent.trim() : '0'
                        };
                    } catch (e) {
                        return null;
                    }
                }
            """)

            # 2. 시간별 날씨 테이블 크롤링
            hourly_data = page.evaluate("""
                () => {
                    const table = document.querySelector('div#hourly .weather_table_wrap table');
                    if (!table) return [];

                    const results = [];
                    const headers = table.querySelectorAll('thead tr._cnTime th._cnItemTime');
                    const tbody = table.querySelector('tbody');
                    const allRows = tbody.querySelectorAll('tr');

                    let probCells = [];
                    let amtCells = [];
                    let humidityCells = [];
                    let windCells = [];

                    allRows.forEach(row => {
                        const text = row.textContent;
                        const cells = row.querySelectorAll('td');

                        if (text.includes('강수확률')) {
                            probCells = Array.from(cells);
                        } else if (text.includes('강수량')) {
                            amtCells = Array.from(cells);
                        } else if (text.includes('습도')) {
                            humidityCells = Array.from(cells);
                        } else if (text.includes('바람')) {
                            windCells = Array.from(cells);
                        }
                    });

                    const minLen = Math.min(headers.length, probCells.length);

                    for (let i = 0; i < minLen; i++) {
                        const th = headers[i];
                        const ymdt = th.getAttribute('data-ymdt') || '';
                        const temp = th.getAttribute('data-tmpr') || '';
                        const status = th.getAttribute('data-wetr-txt') || '';

                        const probText = probCells[i]?.textContent.replace('강수확률', '').trim() || '0';
                        const amtText = amtCells[i]?.textContent.replace('강수량', '').trim() || '-';
                        const humidityText = humidityCells[i]?.textContent.replace('습도', '').trim() || '0';

                        let windDirection = '-';
                        let windSpeed = '0';
                        if (i < windCells.length) {
                            const windText = windCells[i].textContent.replace('바람', '').trim();
                            const parts = windText.split(/\\s+/);
                            if (parts.length >= 2) {
                                windDirection = parts[0];
                                windSpeed = parts[1];
                            }
                        }

                        results.push({
                            ymdt: ymdt,
                            temperature: temp,
                            weather_status: status,
                            precipitation_prob: probText,
                            precipitation_amount: amtText,
                            humidity: humidityText,
                            wind_direction: windDirection,
                            wind_speed: windSpeed
                        });
                    }

                    return results;
                }
            """)

            # 시간별 데이터 처리
            for entry in hourly_data:
                ymdt = entry.get('ymdt', '')
                if len(ymdt) >= 10:
                    # ymdt 형식: YYYYMMDDHH
                    year = int(ymdt[0:4])
                    month = int(ymdt[4:6])
                    day = int(ymdt[6:8])
                    hour = int(ymdt[8:10])
                    date = datetime(year, month, day).date()

                    # 정수 변환
                    temp = int(entry['temperature']) if entry['temperature'] else 0
                    
                    precip_str = entry['precipitation_prob'].replace('%', '') if entry['precipitation_prob'] else '0'
                    precip_prob = int(precip_str) if precip_str.isdigit() else 0
                    
                    humid_str = entry['humidity'].replace('%', '') if entry['humidity'] else '0'
                    humidity = int(humid_str) if humid_str.isdigit() else 0
                    
                    wind_speed_val = float(entry['wind_speed']) if entry['wind_speed'] and entry['wind_speed'] != '-' else 0.0

                    weather_data.append({
                        'region_code': region_code,
                        'date': date,
                        'hour': hour,
                        'temperature': temp,
                        'weather_status': entry['weather_status'],
                        'precipitation_prob': precip_prob,
                        'precipitation_amount': entry['precipitation_amount'],
                        'humidity': humidity,
                        'wind_direction': entry['wind_direction'],
                        'wind_speed': wind_speed_val
                    })

            browser.close()
            print(f"✓ 시간별: {len(weather_data)}개, 현재: {'있음' if current_weather else '없음'}")

        except Exception as e:
            print(f"✗ 크롤링 실패: {e}")
            import traceback
            traceback.print_exc()
            current_weather = None

    return {'hourly': weather_data, 'current': current_weather}


def save_weather_to_db(weather_data_list):
    """
    날씨 데이터를 데이터베이스에 저장

    Args:
        weather_data_list: 크롤링된 날씨 데이터 리스트
    """
    saved_count = 0
    updated_count = 0

    for data in weather_data_list:
        # 기존 데이터 확인
        existing = WeatherData.query.filter_by(
            region_code=data['region_code'],
            date=data['date'],
            hour=data['hour']
        ).first()

        if existing:
            # 업데이트
            existing.temperature = data['temperature']
            existing.weather_status = data['weather_status']
            existing.precipitation_prob = data['precipitation_prob']
            existing.precipitation_amount = data['precipitation_amount']
            existing.humidity = data['humidity']
            existing.wind_direction = data['wind_direction']
            existing.wind_speed = data['wind_speed']
            existing.updated_at = datetime.utcnow()
            updated_count += 1
        else:
            # 새로 저장
            weather = WeatherData(**data)
            db.session.add(weather)
            saved_count += 1

    db.session.commit()
    print(f"✓ DB 저장 완료: {saved_count}개 신규, {updated_count}개 업데이트")


def update_weather_for_region(region_code, weather_url):
    """
    특정 지역의 날씨 데이터 업데이트

    Args:
        region_code: 지역 코드
        weather_url: 네이버 날씨 URL
    """
    print(f"\n{'='*60}")
    print(f"날씨 업데이트: {region_code}")
    print(f"{'='*60}")

    result = crawl_weather(weather_url, region_code)
    
    if result and isinstance(result, dict):
        hourly_data = result.get('hourly', [])
        current_data = result.get('current')
        
        if hourly_data:
            save_weather_to_db(hourly_data)
            return True
    
    return False


def get_morning_weather(region_code, target_date=None):
    """
    새벽 시간(04:00-07:00) 날씨 조회

    Args:
        region_code: 지역 코드
        target_date: 조회할 날짜 (None이면 오늘)

    Returns:
        list: 새벽 날씨 데이터
    """
    if target_date is None:
        target_date = datetime.now().date()

    morning_hours = [4, 5, 6, 7]

    weather_list = WeatherData.query.filter(
        WeatherData.region_code == region_code,
        WeatherData.date == target_date,
        WeatherData.hour.in_(morning_hours)
    ).order_by(WeatherData.hour).all()

    return weather_list


def get_current_weather(region_code):
    """
    현재 시각의 날씨 조회 (없으면 가장 가까운 미래 시각 데이터)

    Args:
        region_code: 지역 코드

    Returns:
        WeatherData: 현재 시각 날씨 데이터
    """
    now = datetime.now()
    current_hour = now.hour
    current_date = now.date()

    # 먼저 현재 시각 데이터 조회
    weather = WeatherData.query.filter(
        WeatherData.region_code == region_code,
        WeatherData.date == current_date,
        WeatherData.hour == current_hour
    ).first()

    # 현재 시각 데이터가 없으면 가장 가까운 미래 시각 조회
    if not weather:
        weather = WeatherData.query.filter(
            WeatherData.region_code == region_code,
            WeatherData.date >= current_date
        ).filter(
            (WeatherData.date > current_date) | (WeatherData.hour > current_hour)
        ).order_by(WeatherData.date, WeatherData.hour).first()

    return weather


def get_today_weather(region_code, target_date=None):
    """
    오늘 하루 날씨 조회 (06:00~23:00)

    Args:
        region_code: 지역 코드
        target_date: 조회할 날짜 (None이면 오늘)

    Returns:
        list: 오늘 날씨 데이터
    """
    if target_date is None:
        target_date = datetime.now().date()

    weather_list = WeatherData.query.filter(
        WeatherData.region_code == region_code,
        WeatherData.date == target_date,
        WeatherData.hour >= 6,
        WeatherData.hour <= 23
    ).order_by(WeatherData.hour).all()

    return weather_list


def get_weather_summary(weather_list):
    """
    날씨 데이터 요약

    Args:
        weather_list: WeatherData 리스트

    Returns:
        dict: 요약 정보
    """
    if not weather_list:
        return None

    temps = [w.temperature for w in weather_list if w.temperature]
    precip_probs = [w.precipitation_prob for w in weather_list if w.precipitation_prob]

    min_temp = min(temps) if temps else 0
    max_temp = max(temps) if temps else 0
    max_precip = max(precip_probs) if precip_probs else 0

    # 가장 많이 나타나는 날씨 상태
    status_list = [w.weather_status for w in weather_list if w.weather_status]
    avg_weather = max(set(status_list), key=status_list.count) if status_list else "알 수 없음"

    # 러닝 추천
    outfit = get_running_outfit(min_temp)

    # 경고 메시지
    warnings = []
    if max_precip >= 40:
        warnings.append("비 올 확률이 높습니다. 실내 운동을 권장합니다.")
    if min_temp <= -7:
        warnings.append("너무 춥습니다. 부상 위험이 있으니 휴식을 권장합니다.")

    return {
        'min_temp': min_temp,
        'max_temp': max_temp,
        'max_precip': max_precip,
        'avg_weather': avg_weather,
        'outfit': outfit,
        'warnings': warnings
    }


def get_weekly_weather(region_code):
    """
    주간 날씨 조회 (7일간)

    Args:
        region_code: 지역 코드

    Returns:
        dict: 날짜별 새벽 날씨 데이터
    """
    from datetime import date, timedelta

    weekly_data = {}
    today = datetime.now().date()

    # 오늘부터 7일간
    for i in range(7):
        target_date = today + timedelta(days=i)
        morning_weather = get_morning_weather(region_code, target_date)
        summary = get_weather_summary(morning_weather)

        weekly_data[target_date] = {
            'weather_list': morning_weather,
            'summary': summary,
            'day_name': get_day_name(target_date)
        }

    return weekly_data


def get_day_name(target_date):
    """
    요일 이름 반환

    Args:
        target_date: 날짜

    Returns:
        str: 요일 이름
    """
    days = ['월', '화', '수', '목', '금', '토', '일']
    return days[target_date.weekday()]


def get_sunrise_sunset(lat, lng, target_date=None):
    """
    일출/일몰 시간 계산

    Args:
        lat: 위도
        lng: 경도
        target_date: 대상 날짜 (None이면 오늘)

    Returns:
        dict: {sunrise: datetime, sunset: datetime}
    """
    from suntime import Sun
    from datetime import date, datetime as dt, timedelta

    if target_date is None:
        target_date = date.today()

    try:
        # float 변환 보장
        lat = float(lat)
        lng = float(lng)

        # date 객체를 datetime 객체로 변환
        if isinstance(target_date, date) and not isinstance(target_date, dt):
            target_datetime = dt.combine(target_date, dt.min.time())
        else:
            target_datetime = target_date

        sun = Sun(lat, lng)
        sunrise_utc = sun.get_sunrise_time(target_datetime)
        sunset_utc = sun.get_sunset_time(target_datetime)

        # 한국 시간으로 변환 (UTC+9)
        kst_offset = timedelta(hours=9)
        sunrise_kst = sunrise_utc + kst_offset
        sunset_kst = sunset_utc + kst_offset

        return {"sunrise": sunrise_kst, "sunset": sunset_kst}
    except Exception as e:
        print(f"일출/일몰 계산 오류 (lat={lat}, lng={lng}): {e}")
        return None
