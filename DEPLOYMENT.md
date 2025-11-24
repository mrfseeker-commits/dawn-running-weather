# Render 배포 가이드

이 문서는 새벽런닝 기상정보 웹앱을 Render에 배포하는 방법을 안내합니다.

## 배포 준비

### 1. Git 저장소 설정

먼저 Git 사용자 정보를 설정합니다 (아직 설정하지 않았다면):

```bash
git config --global user.email "your-email@example.com"
git config --global user.name "Hogun"
```

### 2. GitHub에 코드 업로드

```bash
# 초기 커밋 (이미 git init 완료됨)
git add .
git commit -m "Initial commit - 새벽런닝 기상정보 웹앱"

# GitHub에서 새 레포지토리 생성 후
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Render 배포 단계

### 1. Render 계정 생성

1. [Render](https://render.com)에 접속
2. GitHub 계정으로 로그인/회원가입
3. GitHub 저장소 연결 권한 부여

### 2. 새 Web Service 생성

1. Render 대시보드에서 "New +" 클릭
2. "Web Service" 선택
3. GitHub 저장소 연결 (방금 푸시한 레포지토리 선택)

### 3. 서비스 설정

배포 설정 화면에서 다음 정보를 입력합니다:

#### 기본 설정
- **Name**: `dawn-running-weather` (원하는 이름)
- **Region**: `Oregon (US West)` (무료 플랜에서 가장 빠름)
- **Branch**: `main`
- **Runtime**: `Python 3`

#### Build & Deploy 설정
render.yaml 파일이 자동으로 인식되므로 별도 설정 불필요합니다.

만약 수동 설정이 필요하다면:
- **Build Command**:
  ```bash
  pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium
  ```
- **Start Command**:
  ```bash
  gunicorn app:app
  ```

#### 환경 변수 (Environment Variables)

"Environment" 탭에서 다음 변수들을 설정합니다:

- `PYTHON_VERSION`: `3.11.0`
- `SECRET_KEY`: (자동 생성 또는 직접 입력 - 강력한 랜덤 문자열)
- `FLASK_ENV`: `production`

**SECRET_KEY 생성 방법** (Python에서):
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 4. 플랜 선택

- **Instance Type**: `Free` 선택
- 무료 플랜 제한사항:
  - 15분간 요청이 없으면 자동 슬립
  - 월 750시간 무료 (개인 프로젝트에 충분)
  - 메모리 512MB

### 5. 배포 시작

1. "Create Web Service" 버튼 클릭
2. 자동으로 빌드 시작 (약 5-10분 소요)
3. 로그에서 빌드 진행 상황 확인

## 배포 후 확인사항

### 1. 웹사이트 접속

배포가 완료되면 Render가 제공하는 URL로 접속합니다:
- 형식: `https://your-app-name.onrender.com`

### 2. 데이터베이스 초기화

첫 접속 시 자동으로 SQLite 데이터베이스가 생성됩니다.

### 3. 회원가입 및 테스트

1. 첫 화면에서 회원가입 진행
2. 로그인 후 지역 설정
3. 날씨 데이터 크롤링 확인

## 문제 해결

### Playwright 설치 오류

빌드 로그에서 Playwright 관련 오류가 발생하면:
1. Render 대시보드의 "Environment" 탭 확인
2. Build Command가 올바른지 확인:
   ```bash
   pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium
   ```

### 슬립 모드로 인한 느린 첫 로딩

무료 플랜의 경우 15분간 요청이 없으면 슬립 모드로 전환됩니다.
- 첫 접속 시 30초~1분 정도 소요될 수 있음
- 이후 정상 속도로 동작

### 데이터베이스 초기화

Render는 재배포 시 파일 시스템이 초기화됩니다.
- SQLite 데이터는 재배포 시 사라질 수 있음
- 프로덕션에서는 PostgreSQL 사용 권장 (Render에서 무료 제공)

## 업데이트 배포

코드 수정 후 재배포:

```bash
git add .
git commit -m "업데이트 내용"
git push origin main
```

GitHub에 푸시하면 Render가 자동으로 재배포합니다 (Auto-Deploy 활성화 시).

## 비용

- **무료 플랜**:
  - 개인 프로젝트에 적합
  - 월 750시간 무료 (항상 켜져 있어도 무료)
  - 단, 15분 비활동 시 슬립 모드

- **유료 플랜** ($7/월):
  - 슬립 모드 없음
  - 더 많은 메모리와 CPU
  - 커스텀 도메인 지원

## 도메인 설정 (선택사항)

커스텀 도메인을 사용하려면:
1. Render 대시보드에서 "Settings" → "Custom Domains"
2. 도메인 추가 (예: `weather.yourdomain.com`)
3. DNS 설정에서 CNAME 레코드 추가

## 추가 리소스

- [Render 공식 문서](https://render.com/docs)
- [Flask 배포 가이드](https://flask.palletsprojects.com/en/latest/deploying/)
- [Playwright 문서](https://playwright.dev/python/)

## 참고사항

### 환경별 동작
- **개발 환경**: `python app.py` 실행 시 debug 모드 활성화
- **프로덕션**: Render에서 `FLASK_ENV=production` 설정으로 debug 모드 비활성화

### 보안
- SECRET_KEY는 절대 공개하지 마세요
- GitHub에 .env 파일을 커밋하지 마세요 (.gitignore에 이미 포함됨)

### 데이터 백업
- 중요한 데이터는 정기적으로 백업하세요
- SQLite 파일은 instance/weather.db에 저장됩니다
