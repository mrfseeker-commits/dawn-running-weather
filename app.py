"""
새벽런닝 기상정보 웹 애플리케이션
Flask 메인 애플리케이션
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, init_db, User, SavedLocation, WeatherData
from weather_service import (
    update_weather_for_region,
    get_morning_weather,
    get_current_weather,
    get_today_weather,
    get_weather_summary,
    get_sunrise_sunset,
    get_weekly_weather
)
from realtime_region_code import RealtimeRegionCodeFinder
from runitem.weather_interface import WeatherInterface
from datetime import datetime, timedelta
import os

# Flask 앱 생성
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///weather.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 데이터베이스 초기화
init_db(app)

# Flask-Login 설정
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '로그인이 필요합니다.'

# 지역 코드 검색기 초기화
region_finder = RealtimeRegionCodeFinder()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Jinja2 템플릿 필터 추가
@app.template_filter('korean_date')
def korean_date_filter(date_obj):
    """날짜를 '월 일 요일' 형식으로 변환"""
    if date_obj is None:
        return ''
    days = ['월', '화', '수', '목', '금', '토', '일']
    weekday_name = days[date_obj.weekday()]
    return f"{date_obj.month}월 {date_obj.day}일 {weekday_name}요일"


@app.route('/')
def index():
    """메인 페이지"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        # 유효성 검사
        if not username or not password:
            flash('아이디와 비밀번호를 입력해주세요.', 'danger')
            return render_template('register.html')

        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다.', 'danger')
            return render_template('register.html')

        # 중복 확인
        if User.query.filter_by(username=username).first():
            flash('이미 존재하는 아이디입니다.', 'danger')
            return render_template('register.html')

        # 사용자 생성
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """로그인"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """로그아웃"""
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """대시보드 - 날씨 정보 표시"""
    # 사용자의 저장된 지역 가져오기
    saved_locations = SavedLocation.query.filter_by(user_id=current_user.id).all()

    # 오늘과 내일 날짜
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    # 각 지역의 날씨 정보
    weather_info = []

    for location in saved_locations:
        # 현재 날씨
        current_weather = get_current_weather(location.region_code)
        
        # 오늘 날씨 (하루 전체)
        today_weather = get_today_weather(location.region_code, today)
        today_summary = get_weather_summary(today_weather)

        # 내일 새벽 날씨
        tomorrow_weather = get_morning_weather(location.region_code, tomorrow)
        tomorrow_summary = get_weather_summary(tomorrow_weather)

        # 내일 새벽 런닝 복장 추천 (runitem 모듈 사용)
        outfit_recommendation = None
        if tomorrow_weather:
            # 새벽 날씨 데이터에서 평균값 계산
            temps = [w.temperature for w in tomorrow_weather if w.temperature is not None]
            humidities = [w.humidity for w in tomorrow_weather if w.humidity is not None]
            wind_speeds = [w.wind_speed for w in tomorrow_weather if w.wind_speed is not None]

            if temps:
                avg_temp = sum(temps) / len(temps)
                avg_humidity = sum(humidities) / len(humidities) if humidities else None
                avg_wind_speed = sum(wind_speeds) / len(wind_speeds) if wind_speeds else None

                # WeatherInterface로 복장 추천 받기 (요청마다 새 인스턴스 생성)
                outfit_interface = WeatherInterface()
                weather_data = {
                    'temperature': avg_temp,
                    'humidity': avg_humidity,
                    'wind_speed': avg_wind_speed,
                    'location': location.region_name,
                    'datetime': tomorrow.strftime('%Y-%m-%d')
                }
                outfit_recommendation = outfit_interface.get_outfit_recommendation(weather_data)

        # 일출/일몰 시간 계산
        today_sun = get_sunrise_sunset(location.lat, location.lng, today)
        tomorrow_sun = get_sunrise_sunset(location.lat, location.lng, tomorrow)

        weather_info.append({
            'location': location,
            'current': current_weather,
            'today': {
                'date': today,
                'weather_list': today_weather,
                'summary': today_summary,
                'sunrise': today_sun['sunrise'] if today_sun else None,
                'sunset': today_sun['sunset'] if today_sun else None
            },
            'tomorrow': {
                'date': tomorrow,
                'weather_list': tomorrow_weather,
                'summary': tomorrow_summary,
                'sunrise': tomorrow_sun['sunrise'] if tomorrow_sun else None,
                'sunset': tomorrow_sun['sunset'] if tomorrow_sun else None,
                'outfit_recommendation': outfit_recommendation  # 복장 추천 추가
            }
        })

    return render_template('dashboard.html', weather_info=weather_info, today=today, tomorrow=tomorrow)


@app.route('/settings')
@login_required
def settings():
    """지역 설정 페이지"""
    saved_locations = SavedLocation.query.filter_by(user_id=current_user.id).all()
    return render_template('settings.html', saved_locations=saved_locations)


@app.route('/weekly')
@login_required
def weekly():
    """2일간 새벽날씨 예보 페이지 (내일, 모레)"""
    saved_locations = SavedLocation.query.filter_by(user_id=current_user.id).all()

    # 각 지역의 2일간 날씨 정보
    weekly_info = []
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)

    for location in saved_locations:
        weekly_data = get_weekly_weather(location.region_code)

        # 내일과 모레만 필터링 (2일간)
        filtered_data = {k: v for k, v in weekly_data.items() if k in [tomorrow, day_after_tomorrow]}

        # 각 날짜별 일출시간 추가
        for target_date, data in filtered_data.items():
            sun_info = get_sunrise_sunset(location.lat, location.lng, target_date)
            if sun_info:
                data['sunrise'] = sun_info['sunrise']
                data['sunset'] = sun_info['sunset']

        weekly_info.append({
            'location': location,
            'weekly_data': filtered_data
        })

    return render_template('weekly.html', weekly_info=weekly_info)


# ===== API 엔드포인트 =====

@app.route('/api/search_region', methods=['POST'])
@login_required
def api_search_region():
    """지역 검색 API"""
    keyword = request.json.get('keyword', '')

    if not keyword:
        return jsonify({'error': '검색어를 입력해주세요.'}), 400

    try:
        # 엑셀에서 지역 검색
        addresses = region_finder.search_address(keyword)

        # 최대 20개까지만
        results = addresses[:20]

        return jsonify({
            'success': True,
            'results': results,
            'total': len(addresses)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add_location', methods=['POST'])
@login_required
def api_add_location():
    """지역 추가 API"""
    data = request.json
    region_name = data.get('region_name')
    lat = data.get('lat')
    lng = data.get('lng')
    alias = data.get('alias', '').strip()  # 별칭 (옵션)

    if not all([region_name, lat, lng]):
        return jsonify({'error': '필수 정보가 누락되었습니다.'}), 400

    try:
        # 최대 저장 개수 확인 (5개)
        current_count = SavedLocation.query.filter_by(user_id=current_user.id).count()
        if current_count >= 5:
            return jsonify({'error': '최대 5개까지만 저장할 수 있습니다.'}), 400

        # 지역명 중복 확인 (같은 이름의 지역이 이미 있는지)
        existing_by_name = SavedLocation.query.filter_by(
            user_id=current_user.id,
            region_name=region_name
        ).first()

        if existing_by_name:
            return jsonify({'error': f'"{region_name}"은(는) 이미 저장된 지역입니다.'}), 400

        # 지역 코드 조회
        print(f"[지역 추가] 지역명: {region_name}, 위도: {lat}, 경도: {lng}")
        # API 대신 Playwright로 지역명 검색하여 코드 획득
        region_code = region_finder.get_region_code(region_name, lat, lng, delay=0.5)
        print(f"[지역 추가] 조회된 지역 코드: {region_code}")

        if not region_code:
            return jsonify({'error': '지역 코드를 찾을 수 없습니다. 네이버 API 오류가 발생했습니다.'}), 404

        # 저장
        location = SavedLocation(
            user_id=current_user.id,
            region_name=region_name,
            region_code=region_code,
            lat=float(lat),
            lng=float(lng),
            alias=alias if alias else None
        )
        db.session.add(location)
        db.session.commit()

        # 날씨 데이터 크롤링 (비동기 처리)
        weather_url = f"https://weather.naver.com/today/{region_code}"
        
        # 스레드로 백그라운드 실행
        import threading
        thread = threading.Thread(target=update_weather_for_region, args=(region_code, weather_url))
        thread.daemon = True  # 메인 스레드 종료 시 함께 종료
        thread.start()

        return jsonify({
            'success': True,
            'message': '지역이 추가되었습니다.',
            'location': {
                'id': location.id,
                'name': location.region_name,
                'code': location.region_code
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete_location/<int:location_id>', methods=['DELETE'])
@login_required
def api_delete_location(location_id):
    """지역 삭제 API"""
    location = SavedLocation.query.get_or_404(location_id)

    # 권한 확인
    if location.user_id != current_user.id:
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        db.session.delete(location)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '지역이 삭제되었습니다.'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/update_weather/<int:location_id>', methods=['POST'])
@login_required
def api_update_weather(location_id):
    """특정 지역 날씨 수동 업데이트 API"""
    location = SavedLocation.query.get_or_404(location_id)

    # 권한 확인
    if location.user_id != current_user.id:
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        weather_url = f"https://weather.naver.com/today/{location.region_code}"
        success = update_weather_for_region(location.region_code, weather_url)

        if success:
            return jsonify({
                'success': True,
                'message': '날씨 정보가 업데이트되었습니다.'
            })
        else:
            return jsonify({'error': '날씨 정보 업데이트에 실패했습니다.'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/update_all_weather', methods=['POST'])
@login_required
def api_update_all_weather():
    """전체 지역 날씨 수동 업데이트 API"""
    try:
        saved_locations = SavedLocation.query.filter_by(user_id=current_user.id).all()

        if not saved_locations:
            return jsonify({'error': '저장된 지역이 없습니다.'}), 400

        success_count = 0
        failed_count = 0

        print(f"\n[전체 업데이트] {len(saved_locations)}개 지역 업데이트 시작")

        for location in saved_locations:
            try:
                weather_url = f"https://weather.naver.com/today/{location.region_code}"
                result = update_weather_for_region(location.region_code, weather_url)

                if result:
                    success_count += 1
                    print(f"✓ {location.region_name} 업데이트 완료")
                else:
                    failed_count += 1
                    print(f"✗ {location.region_name} 업데이트 실패")
            except Exception as e:
                failed_count += 1
                print(f"✗ {location.region_name} 오류: {e}")

        print(f"[전체 업데이트] 완료 - 성공: {success_count}, 실패: {failed_count}\n")

        return jsonify({
            'success': True,
            'message': f'전체 업데이트 완료 (성공: {success_count}, 실패: {failed_count})',
            'success_count': success_count,
            'failed_count': failed_count
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # 스케줄러 초기화 (자동 날씨 업데이트)
    from scheduler import init_scheduler
    scheduler = init_scheduler(app)

    try:
        # 프로덕션 환경 확인
        is_production = os.environ.get('FLASK_ENV') == 'production'
        app.run(debug=not is_production, host='0.0.0.0', port=5001)
    except (KeyboardInterrupt, SystemExit):
        # 앱 종료 시 스케줄러도 종료
        scheduler.shutdown()
        print('\n앱이 종료되었습니다.')
