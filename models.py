"""
데이터베이스 모델
- User: 사용자 정보
- SavedLocation: 사용자가 저장한 지역
- WeatherData: 크롤링된 날씨 데이터
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """사용자 모델"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)  # 이메일 주소
    email_notification = db.Column(db.Boolean, default=False)  # 이메일 알림 설정
    notification_time = db.Column(db.String(5), default='20:00')  # 알림 시간 (HH:MM)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    saved_locations = db.relationship('SavedLocation', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """비밀번호 해싱"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """비밀번호 확인"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class SavedLocation(db.Model):
    """사용자가 저장한 지역"""
    __tablename__ = 'saved_locations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    region_name = db.Column(db.String(200), nullable=False)  # 예: "대전광역시 유성구 송강동"
    region_code = db.Column(db.String(20), nullable=False)   # 예: "07200147"
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    alias = db.Column(db.String(100), nullable=True)  # 별칭 (예: "우리동네")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SavedLocation {self.region_name}>'


class WeatherData(db.Model):
    """크롤링된 날씨 데이터"""
    __tablename__ = 'weather_data'

    id = db.Column(db.Integer, primary_key=True)
    region_code = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)  # 날짜
    hour = db.Column(db.Integer, nullable=False)  # 시간 (0-23)

    # 날씨 정보
    temperature = db.Column(db.Integer)  # 기온
    weather_status = db.Column(db.String(50))  # 날씨 상태 (맑음, 흐림 등)
    precipitation_prob = db.Column(db.Integer)  # 강수확률 (%)
    precipitation_amount = db.Column(db.String(20))  # 강수량
    humidity = db.Column(db.Integer)  # 습도 (%)
    wind_direction = db.Column(db.String(20))  # 풍향
    wind_speed = db.Column(db.Float)  # 풍속 (m/s)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 복합 유니크 제약조건: 같은 지역, 날짜, 시간은 하나만
    __table_args__ = (
        db.UniqueConstraint('region_code', 'date', 'hour', name='_region_date_hour_uc'),
    )

    def __repr__(self):
        return f'<WeatherData {self.region_code} {self.date} {self.hour}:00>'


class OutfitRecommendation(db.Model):
    """복장 추천 데이터베이스 (사용자 커스터마이징 가능)"""
    __tablename__ = 'outfit_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # None이면 기본 추천

    # 조건
    min_temp = db.Column(db.Integer)  # 최저 기온
    max_temp = db.Column(db.Integer, nullable=True)  # 최대 기온 (범위 지정용)
    weather_condition = db.Column(db.String(50), nullable=True)  # 날씨 조건 (맑음, 흐림, 비 등)
    min_wind_speed = db.Column(db.Float, nullable=True)  # 최소 풍속
    max_wind_speed = db.Column(db.Float, nullable=True)  # 최대 풍속

    # 추천 복장
    outfit_description = db.Column(db.Text, nullable=False)  # 복장 설명

    # 우선순위 (낮을수록 우선)
    priority = db.Column(db.Integer, default=100)

    # 활성화 여부
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<OutfitRecommendation {self.min_temp}°C: {self.outfit_description[:20]}>'

    def matches(self, temp, weather=None, wind_speed=None):
        """
        현재 조건과 매칭되는지 확인

        Args:
            temp: 기온
            weather: 날씨 상태
            wind_speed: 풍속

        Returns:
            bool: 매칭 여부
        """
        # 기온 체크
        if self.max_temp:
            if not (self.min_temp <= temp < self.max_temp):
                return False
        else:
            if temp < self.min_temp:
                return False

        # 날씨 조건 체크
        if self.weather_condition and weather:
            if self.weather_condition not in weather:
                return False

        # 풍속 체크
        if self.min_wind_speed and wind_speed:
            if wind_speed < self.min_wind_speed:
                return False
        if self.max_wind_speed and wind_speed:
            if wind_speed >= self.max_wind_speed:
                return False

        return True


def init_db(app):
    """데이터베이스 초기화"""
    db.init_app(app)

    with app.app_context():
        # 테이블 생성
        db.create_all()
        print("✓ 데이터베이스 초기화 완료")
