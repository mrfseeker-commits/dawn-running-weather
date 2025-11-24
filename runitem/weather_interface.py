"""
기상 정보 크롤링 프로그램 연동 인터페이스

이 모듈은 외부 기상 정보 크롤링 프로그램과 런닝 복장 추천 시스템을 연동하기 위한
인터페이스를 제공합니다.
"""

from .database import RunningOutfitDB
from typing import Dict, List, Tuple, Optional


class WeatherInterface:
    """기상 정보와 복장 추천 시스템을 연동하는 인터페이스"""

    def __init__(self):
        self.db = RunningOutfitDB()
        self.db.connect()

    def __del__(self):
        """객체 소멸 시 데이터베이스 연결 종료"""
        if hasattr(self, 'db'):
            self.db.close()

    def get_outfit_recommendation(self, weather_data: Dict) -> Dict:
        """
        기상 데이터를 받아 복장 추천을 반환합니다.

        Parameters:
        -----------
        weather_data : dict
            기상 정보를 담은 딕셔너리
            필수 키:
                - temperature (float): 기온 (°C)
            선택 키:
                - humidity (float): 습도 (%)
                - wind_speed (float): 풍속 (m/s)
                - location (str): 지역명 (정보용)
                - datetime (str): 날짜/시간 (정보용)

        Returns:
        --------
        dict
            복장 추천 결과
            {
                'status': 'success' | 'warning' | 'error',
                'location': str (있는 경우),
                'datetime': str (있는 경우),
                'weather': {
                    'temperature': float,
                    'humidity': float | None,
                    'wind_speed': float | None
                },
                'recommendations': [
                    {
                        'top': str,
                        'bottom': str,
                        'accessories': str,
                        'notes': str,
                        'temp_range': str
                    },
                    ...
                ]
            }

        Examples:
        ---------
        >>> interface = WeatherInterface()
        >>> weather = {
        ...     'temperature': 18.5,
        ...     'humidity': 65,
        ...     'wind_speed': 3.2,
        ...     'location': '서울',
        ...     'datetime': '2025-11-23 18:00'
        ... }
        >>> result = interface.get_outfit_recommendation(weather)
        >>> print(result['recommendations'][0]['top'])
        """
        # 필수 값 확인
        if 'temperature' not in weather_data:
            return {
                'status': 'error',
                'message': '기온(temperature) 정보가 필요합니다.'
            }

        temperature = weather_data['temperature']
        humidity = weather_data.get('humidity')
        wind_speed = weather_data.get('wind_speed')
        location = weather_data.get('location', '알 수 없음')
        datetime_str = weather_data.get('datetime', '알 수 없음')

        # 복장 추천 조회
        results = self.db.get_recommendation(temperature, humidity, wind_speed)

        # 결과 포맷팅
        recommendations = []
        status = 'success'

        for result in results:
            top, bottom, accessories, notes, temp_min, temp_max = result

            # 극한 기온 체크
            if top == "실외 런닝 부적절":
                status = 'warning'

            recommendations.append({
                'top': top,
                'bottom': bottom,
                'accessories': accessories,
                'notes': notes,
                'temp_range': f"{temp_min}°C ~ {temp_max}°C"
            })

        return {
            'status': status,
            'location': location,
            'datetime': datetime_str,
            'weather': {
                'temperature': temperature,
                'humidity': humidity,
                'wind_speed': wind_speed
            },
            'recommendations': recommendations
        }

    def get_simple_recommendation(self, temperature: float,
                                  humidity: float = None,
                                  wind_speed: float = None) -> List[Dict]:
        """
        간단한 형태로 복장 추천을 반환합니다.

        Parameters:
        -----------
        temperature : float
            기온 (°C)
        humidity : float, optional
            습도 (%)
        wind_speed : float, optional
            풍속 (m/s)

        Returns:
        --------
        list of dict
            추천 복장 리스트
        """
        results = self.db.get_recommendation(temperature, humidity, wind_speed)

        recommendations = []
        for result in results:
            top, bottom, accessories, notes, temp_min, temp_max = result
            recommendations.append({
                'top': top,
                'bottom': bottom,
                'accessories': accessories,
                'notes': notes,
                'temp_range': f"{temp_min}°C ~ {temp_max}°C"
            })

        return recommendations

    def format_recommendation_text(self, weather_data: Dict) -> str:
        """
        복장 추천을 사람이 읽기 쉬운 텍스트로 포맷팅합니다.

        Parameters:
        -----------
        weather_data : dict
            기상 정보를 담은 딕셔너리

        Returns:
        --------
        str
            포맷팅된 추천 텍스트
        """
        result = self.get_outfit_recommendation(weather_data)

        if result['status'] == 'error':
            return result['message']

        # 헤더
        text = "="*60 + "\n"
        text += "런닝 복장 추천\n"
        text += "="*60 + "\n\n"

        # 기상 정보
        text += f"위치: {result['location']}\n"
        text += f"시간: {result['datetime']}\n\n"

        weather = result['weather']
        text += f"기온: {weather['temperature']}°C"
        if weather['humidity'] is not None:
            text += f" | 습도: {weather['humidity']}%"
        if weather['wind_speed'] is not None:
            text += f" | 풍속: {weather['wind_speed']}m/s"
        text += "\n\n"

        # 경고 메시지
        if result['status'] == 'warning':
            text += "⚠️  경고: 극한 기온입니다!\n\n"

        # 추천 복장
        text += "-"*60 + "\n"
        for idx, rec in enumerate(result['recommendations'], 1):
            if len(result['recommendations']) > 1:
                text += f"\n[ 추천 {idx} ] ({rec['temp_range']})\n"

            text += f"상의: {rec['top']}\n"
            text += f"하의: {rec['bottom']}\n"

            if rec['accessories']:
                text += f"액세서리: {rec['accessories']}\n"

            if rec['notes']:
                text += f"\n{rec['notes']}\n"

            if idx < len(result['recommendations']):
                text += "\n" + "-"*60 + "\n"

        text += "\n" + "="*60 + "\n"

        return text


# 사용 예시
if __name__ == "__main__":
    # 인터페이스 생성
    interface = WeatherInterface()

    # 예시 1: 딕셔너리 형태로 전달
    print("=== 예시 1: 딕셔너리 형태 ===\n")
    weather_data = {
        'temperature': 18.5,
        'humidity': 65,
        'wind_speed': 3.2,
        'location': '서울 강남',
        'datetime': '2025-11-23 18:00'
    }

    result = interface.get_outfit_recommendation(weather_data)
    print(f"상태: {result['status']}")
    print(f"위치: {result['location']}")
    print(f"시간: {result['datetime']}")
    print(f"\n추천 개수: {len(result['recommendations'])}개")

    for idx, rec in enumerate(result['recommendations'], 1):
        print(f"\n추천 {idx}:")
        print(f"  상의: {rec['top']}")
        print(f"  하의: {rec['bottom']}")

    # 예시 2: 간단한 형태
    print("\n\n=== 예시 2: 간단한 형태 ===\n")
    recommendations = interface.get_simple_recommendation(12.0, 70, 5)
    for rec in recommendations:
        print(f"상의: {rec['top']}")
        print(f"하의: {rec['bottom']}")

    # 예시 3: 텍스트 포맷팅
    print("\n\n=== 예시 3: 텍스트 포맷팅 ===\n")
    weather_data_2 = {
        'temperature': 32,
        'humidity': 75,
        'wind_speed': 2,
        'location': '부산 해운대',
        'datetime': '2025-07-15 14:00'
    }

    formatted_text = interface.format_recommendation_text(weather_data_2)
    print(formatted_text)
