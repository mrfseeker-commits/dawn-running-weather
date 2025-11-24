# 기상 크롤링 프로그램 연동 가이드

런닝 복장 추천 시스템과 기상 정보 크롤링 프로그램을 연동하는 방법입니다.

## 핵심 파일

- `database.py` - 데이터베이스 핵심 로직
- `weather_interface.py` - 기상 프로그램 연동 인터페이스
- `running_outfits.db` - 15개 복장 데이터 (자동 생성됨)

## 빠른 시작

### 1. 기본 사용법

```python
from weather_interface import WeatherInterface

# 인터페이스 생성
interface = WeatherInterface()

# 기상 데이터 입력
weather_data = {
    'temperature': 7.5,       # 필수: 기온
    'humidity': 65,           # 선택: 습도 (고습도 시 속건성 추천)
    'wind_speed': 3.2,        # 선택: 풍속 (강풍 시 방풍/보온 강화)
    'location': '서울',       # 선택: 표시용
    'datetime': '2025-11-23'  # 선택: 표시용
}

# 복장 추천 받기
result = interface.get_outfit_recommendation(weather_data)

# 결과 사용
print(f"상태: {result['status']}")  # success, warning, error
print(f"상의: {result['recommendations'][0]['top']}")
print(f"장갑/액세서리: {result['recommendations'][0]['accessories']}")
```

### 2. 주요 변경 사항 (2025-11 업데이트)

새로운 추천 로직이 적용되었습니다:
- **런닝 조끼(Vest)**: 0~10°C 구간에서 적극 추천 (체온 조절 용이)
- **장갑 세분화**:
    - **7~10°C**: 얇은 손가락 장갑
    - **0~7°C**: 보온 장갑
    - **0°C 미만**: 두꺼운 방한 장갑

## 특수 기능 및 경고

### 1. 극한 기온 경고 (Safety First)

다음 조건에서는 `status`가 `'warning'`으로 반환되며, 실내 운동을 권장합니다.

- **고온 경고**: **29°C 이상** (열사병 위험)
- **저온 경고**: **-7°C 이하** (동상 위험)

```python
if result['status'] == 'warning':
    print("⚠️  경고: 실외 운동 부적절")
    print(result['recommendations'][0]['notes'])
    # 예: "현재 기온 30°C - 매우 더운 날씨로 열사병 위험..."
```

### 2. 고습도 대응

- 습도가 높을 경우(예: 70% 이상), 기온이 적당하더라도 **속건성/메쉬 소재**를 우선 추천합니다.

## 웹 API 서버 예시

Flask를 사용한 간단한 API 서버:

```python
from flask import Flask, request, jsonify
from weather_interface import WeatherInterface

app = Flask(__name__)
interface = WeatherInterface()

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    result = interface.get_outfit_recommendation(data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
```

**요청:**
```bash
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"temperature": 18.5, "humidity": 65, "wind_speed": 3.2}'
```

## 에러 처리

```python
result = interface.get_outfit_recommendation(weather_data)

if result['status'] == 'error':
    print(f"에러: {result['message']}")
elif result['status'] == 'warning':
    print("⚠️ 극한 기온 경고")
else:
    print("정상 추천")
```

## 주의사항

1. **필수 값**: `temperature`는 반드시 제공해야 합니다
2. **단위**: 기온(°C), 습도(%), 풍속(m/s)
3. **데이터베이스**: `running_outfits.db` 파일이 자동 생성됩니다
4. **연결 관리**: WeatherInterface 객체는 자동으로 DB 연결을 관리합니다

## 테스트

```bash
python weather_interface.py
```

위 명령어로 3가지 예시를 확인할 수 있습니다.
