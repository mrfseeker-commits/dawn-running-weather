# 🌅 새벽런닝 기상정보

새벽 러너를 위한 맞춤형 기상정보 및 런닝 복장 추천 웹 애플리케이션

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 주요 기능

### 🌤️ 날씨 정보
- **실시간 날씨**: 현재 기온, 날씨 상태, 강수확률
- **내일 새벽 예보**: 04:00~07:00 시간대 상세 날씨
- **2일간 예보**: 내일/모레 새벽 날씨 비교
- **일출 시간**: 자동 계산된 일출 시간 제공

### 👕 스마트 복장 추천
- **온도별 맞춤 추천**: 15단계 세분화된 복장 데이터베이스
- **습도/풍속 고려**: 체감온도를 반영한 정확한 추천
- **장갑 세분화**: 
  - 7~10°C: 얇은 손가락 장갑
  - 0~7°C: 보온 장갑
  - 0°C 미만: 두꺼운 방한 장갑
- **런닝 조끼 추천**: 0~10°C 구간에서 체온 조절용 조끼 추천
- **극한 기온 경고**: 29°C 이상, -7°C 이하 시 실내 운동 권장

### 🎨 사용자 경험
- **다크모드 지원**: 시스템 테마 자동 감지
- **반응형 디자인**: 모바일/데스크톱 최적화
- **최대 5개 지역**: 관심 지역 등록 및 관리
- **자동 업데이트**: 스케줄러를 통한 자동 날씨 갱신

## 🚀 빠른 시작

### 필수 요구사항
- Python 3.9 이상
- pip (Python 패키지 관리자)

### 설치 방법

1. **저장소 클론**
```bash
git clone https://github.com/YOUR_USERNAME/weatherccc.git
cd weatherccc
```

2. **가상환경 생성 및 활성화** (권장)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **의존성 패키지 설치**
```bash
pip install -r requirements.txt
```

4. **Playwright 브라우저 설치** (네이버 날씨 크롤링용)
```bash
playwright install chromium
```

5. **애플리케이션 실행**
```bash
python app.py
```

6. **웹 브라우저에서 접속**
```
http://localhost:5001
```

## 📚 사용 방법

### 1. 회원가입 및 로그인
- 첫 방문 시 회원가입 필요
- 아이디와 비밀번호로 간단하게 가입

### 2. 지역 설정
- **지역 설정** 메뉴에서 관심 지역 추가
- 지역명 검색 (예: "서울 강남구", "부산 해운대구")
- 최대 5개 지역까지 등록 가능
- 각 지역에 별칭(닉네임) 설정 가능

### 3. 대시보드 확인
- 현재 날씨 및 오늘 날씨 요약
- **내일 새벽 날씨** (04:00~07:00)
  - 시간별 상세 정보
  - 일출 시간
  - **런닝 복장 추천** (상의/하의/장갑·액세서리)
  - 날씨 경고 (비, 추위)

### 4. 2일간 예보
- 내일과 모레 새벽 날씨 한눈에 비교
- 테이블 형식으로 정리된 정보

## 🛠️ 기술 스택

### Backend
- **Flask**: 웹 프레임워크
- **SQLAlchemy**: ORM 데이터베이스
- **Flask-Login**: 사용자 인증
- **APScheduler**: 자동 날씨 업데이트

### Frontend
- **Bootstrap 5**: UI 프레임워크
- **Bootstrap Icons**: 아이콘
- **Jinja2**: 템플릿 엔진

### Data Collection
- **Playwright**: 네이버 날씨 크롤링
- **openpyxl**: 행정구역 데이터 처리
- **suntime**: 일출/일몰 시간 계산

### Outfit Recommendation
- **SQLite**: 복장 추천 데이터베이스 (15단계)
- **Custom Algorithm**: 온도/습도/풍속 기반 추천 로직

## 📁 프로젝트 구조

```
weatherccc/
├── app.py                      # Flask 메인 애플리케이션
├── models.py                   # 데이터베이스 모델
├── weather_service.py          # 날씨 크롤링 및 처리
├── scheduler.py                # 자동 업데이트 스케줄러
├── realtime_region_code.py     # 지역 코드 검색
├── runitem/                    # 런닝 복장 추천 시스템
│   ├── database.py            # 복장 DB 관리
│   ├── weather_interface.py   # 외부 연동 인터페이스
│   └── INTEGRATION_GUIDE.md   # 연동 가이드
├── templates/                  # HTML 템플릿
│   ├── base.html
│   ├── dashboard.html
│   ├── weekly.html
│   ├── settings.html
│   └── ...
├── static/                     # 정적 파일
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── requirements.txt            # Python 의존성
└── 행정구역별_위경도_좌표.xlsx  # 지역 데이터
```

## ⚙️ 설정

### 데이터베이스 초기화
앱 첫 실행 시 자동으로 데이터베이스가 생성됩니다.
- `weather.db`: 메인 데이터베이스 (사용자, 지역, 날씨)
- `running_outfits.db`: 복장 추천 데이터베이스

### 스케줄러
- **매일 자정**: 전체 날씨 업데이트
- **10분마다**: 날씨 갱신

## 🔒 보안

- 비밀번호는 Werkzeug를 사용하여 해시화
- SECRET_KEY는 프로덕션 환경에서 반드시 변경 필요
- CSRF 보호 활성화
- SQL Injection 방지 (SQLAlchemy ORM 사용)

## 🤝 기여하기

이슈 및 풀 리퀘스트를 환영합니다!

1. 이 저장소를 Fork
2. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 Push (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📝 라이선스

MIT License - 자유롭게 사용하세요!

## 👤 제작자

**Hogun**
- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)

## 🙏 감사의 말

- 네이버 날씨: 날씨 데이터 제공
- 한국 러닝 커뮤니티: 복장 추천 데이터 참고

## 📧 문의

질문이나 제안사항이 있으시면 GitHub Issues를 이용해주세요.

---

**© 2025.11 by Hogun** | 네이버 날씨 데이터 기반
