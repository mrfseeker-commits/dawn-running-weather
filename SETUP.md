# 🚀 새벽런닝 기상정보 앱 - 설치 및 실행 가이드

## 📋 사전 요구사항

- Python 3.9 이상
- Git

## 🔧 설치 방법

### 1. 의존성 패키지 설치

```bash
cd C:\Users\user\Documents\cursor\weather2
pip install -r requirements.txt
```

### 2. Playwright 브라우저 설치

```bash
playwright install chromium
```

## ▶️ 실행 방법

### 방법 1: 직접 실행

```bash
python app.py
```

### 방법 2: Flask CLI 사용

```bash
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
```

웹 브라우저에서 `http://localhost:5000` 접속

## 📱 사용 방법

### 1️⃣ 회원가입
- 첫 방문 시 회원가입 (`http://localhost:5000/register`)
- 아이디와 비밀번호 설정 (간단한 정보만 필요)

### 2️⃣ 지역 추가
1. 로그인 후 "지역 설정" 메뉴 클릭
2. 검색창에 지역 입력 (예: "대전 유성구 송강동")
3. 검색 결과에서 원하는 지역 선택하여 추가
4. 최대 5개까지 저장 가능

### 3️⃣ 대시보드 확인
- "대시보드" 메뉴에서 새벽 날씨 확인
- 오늘과 내일 04:00~06:00 시간대 날씨 표시
- 기온별 러닝 복장 추천 제공
- 강수확률 높으면 경고 표시

## 🔄 자동 업데이트

앱 실행 시 자동으로 스케줄러가 시작됩니다:

- **매일 자정 (00:00)**: 다음날 날씨 데이터 크롤링
- **3시간마다**: 기존 날씨 데이터 갱신

## 🗄️ 데이터베이스

SQLite 데이터베이스 파일: `weather.db`

- 첫 실행 시 자동 생성
- 사용자 정보, 저장된 지역, 날씨 데이터 저장

## ⚙️ 환경 설정

### SECRET_KEY 변경 (프로덕션 배포 시)

`app.py` 파일에서 아래 부분 수정:

```python
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
```

더 안전한 랜덤 키로 변경:

```python
import secrets
secrets.token_hex(32)  # 이 값을 사용
```

### 포트 변경

`app.py` 파일 마지막 부분:

```python
app.run(debug=True, host='0.0.0.0', port=5000)  # port 숫자 변경
```

## 🐛 문제 해결

### 1. 모듈을 찾을 수 없음 (ModuleNotFoundError)
```bash
pip install -r requirements.txt
```

### 2. Playwright 브라우저 오류
```bash
playwright install chromium
```

### 3. 데이터베이스 오류
기존 `weather.db` 파일 삭제 후 재실행

### 4. 포트 이미 사용 중
다른 포트 번호로 변경 또는 기존 프로세스 종료

## 📊 프로젝트 구조

```
weather2/
├── app.py                      # Flask 메인 앱
├── models.py                   # DB 모델
├── weather_service.py          # 날씨 크롤링
├── scheduler.py                # 자동 스케줄러
├── realtime_region_code.py     # 지역 검색
├── 행정구역별_위경도_좌표.xlsx  # 21,816개 행정구역 데이터
├── static/                     # CSS, JS
├── templates/                  # HTML 템플릿
└── weather.db                  # SQLite DB (자동 생성)
```

## 🔐 보안 주의사항

- 프로덕션 배포 시 `SECRET_KEY` 반드시 변경
- `DEBUG=False`로 설정
- HTTPS 사용 권장
- 정기적인 데이터베이스 백업

## 🌟 주요 기능

✅ 전국 21,816개 행정구역 검색
✅ 새벽 시간(04:00-06:00) 날씨 정보
✅ 기온별 러닝 복장 자동 추천
✅ 강수확률 40% 이상 시 경고
✅ 자동 날씨 업데이트 (매일 자정 & 3시간마다)
✅ 반응형 웹 디자인 (모바일 지원)

## 📞 문의

GitHub Issues: [YOUR_REPO_URL]

---

**Happy Running! 🏃‍♂️**
