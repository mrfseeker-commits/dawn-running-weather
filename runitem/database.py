import sqlite3
from typing import List, Tuple, Optional

class RunningOutfitDB:
    def __init__(self, db_name: str = "running_outfits.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        """데이터베이스 연결"""
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """테이블 생성"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS outfit_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temp_min REAL NOT NULL,
                temp_max REAL NOT NULL,
                humidity_min REAL,
                humidity_max REAL,
                wind_speed_min REAL,
                wind_speed_max REAL,
                top TEXT NOT NULL,
                bottom TEXT NOT NULL,
                accessories TEXT,
                notes TEXT
            )
        ''')
        self.conn.commit()

    def add_outfit(self, temp_min: float, temp_max: float,
                   humidity_min: float = None, humidity_max: float = None,
                   wind_speed_min: float = None, wind_speed_max: float = None,
                   top: str = "", bottom: str = "",
                   accessories: str = "", notes: str = ""):
        """복장 추천 데이터 추가"""
        self.cursor.execute('''
            INSERT INTO outfit_recommendations
            (temp_min, temp_max, humidity_min, humidity_max, wind_speed_min, wind_speed_max,
             top, bottom, accessories, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (temp_min, temp_max, humidity_min, humidity_max, wind_speed_min, wind_speed_max,
              top, bottom, accessories, notes))
        self.conn.commit()

    def get_recommendation(self, temperature: float,
                          humidity: float = None,
                          wind_speed: float = None) -> List[Tuple]:
        """기상 조건에 맞는 복장 추천"""
        # 극한 기온 체크 - 실외 런닝 부적절
        if temperature >= 29:
            return [("실외 런닝 부적절", "실내 운동 권장",
                    "",
                    f"현재 기온 {temperature}°C - 매우 더운 날씨로 열사병, 탈수 위험이 높습니다. "
                    "실내 트레드밀이나 에어컨이 있는 체육관에서 운동하시거나, "
                    "이른 아침(5-7시) 또는 늦은 저녁(20-22시) 시간대를 이용하세요.",
                    temperature, temperature)]

        if temperature <= -7:
            return [("실외 런닝 부적절", "실내 운동 권장",
                    "",
                    f"현재 기온 {temperature}°C - 매우 추운 날씨로 동상, 저체온증 위험이 높습니다. "
                    "실내 트레드밀이나 체육관에서 운동하시거나, "
                    "낮 시간대(12-14시) 기온이 상승할 때를 이용하세요.",
                    temperature, temperature)]

        query = '''
            SELECT top, bottom, accessories, notes, temp_min, temp_max
            FROM outfit_recommendations
            WHERE temp_min <= ? AND temp_max >= ?
        '''
        params = [temperature, temperature]

        if humidity is not None:
            query += ' AND (humidity_min IS NULL OR humidity_min <= ?) AND (humidity_max IS NULL OR humidity_max >= ?)'
            params.extend([humidity, humidity])

        if wind_speed is not None:
            query += ' AND (wind_speed_min IS NULL OR wind_speed_min <= ?) AND (wind_speed_max IS NULL OR wind_speed_max >= ?)'
            params.extend([wind_speed, wind_speed])

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_all_outfits(self) -> List[Tuple]:
        """모든 복장 데이터 조회"""
        self.cursor.execute('SELECT * FROM outfit_recommendations')
        return self.cursor.fetchall()

    def delete_outfit(self, outfit_id: int):
        """복장 데이터 삭제"""
        self.cursor.execute('DELETE FROM outfit_recommendations WHERE id = ?', (outfit_id,))
        self.conn.commit()

    def initialize_sample_data(self):
        """
        한국 러닝 커뮤니티 및 스포츠 브랜드 추천을 기반으로 한 샘플 데이터
        출처: 러닝 커뮤니티, 나이키 코리아, MO Sports 등
        """
        sample_data = [
            # 25도 이상 - 한여름
            (25, 35, 0, 60, 0, 10,
             "싱글렛 또는 민소매 러닝 셔츠", "러닝 반바지",
             "선글라스, 모자, 선크림, 얇은 헤드밴드",
             "매우 더운 날씨 - 통풍이 잘 되는 옷 착용, UV 차단 중요"),

            (25, 35, 60, 100, 0, 10,
             "속건성 민소매 또는 메쉬 반팔 티셔츠", "러닝 반바지",
             "땀 흡수 헤드밴드, 선글라스, 모자, 선크림",
             "고온 다습 - 통풍과 땀 배출이 중요, 수분 보충 필수"),

            # 20-25도 - 초여름/초가을
            (20, 25, 0, 100, 0, 15,
             "반팔 티셔츠 또는 싱글렛", "러닝 반바지",
             "선글라스, 얇은 헤드밴드",
             "러닝하기 가장 좋은 날씨, 반팔+반바지면 충분"),

            # 15-20도 - 선선한 봄/가을
            (15, 20, 0, 100, 0, 10,
             "반팔 티셔츠 또는 얇은 긴팔", "러닝 반바지",
             "암슬리브 (필요시)",
             "쾌적한 런닝 날씨, 초반 약간 쌀쌀할 수 있음"),

            (15, 20, 0, 100, 10, 20,
             "반팔 티셔츠 + 얇은 바람막이", "러닝 반바지 또는 타이즈",
             "암슬리브, 버프",
             "바람이 강한 날 - 얇은 바람막이 추천"),

            # 10-15도 - 쌀쌀한 날씨
            (10, 15, 0, 100, 0, 10,
             "얇은 긴팔 티셔츠", "롱 타이즈 또는 반바지",
             "얇은 장갑 (선택)",
             "반팔+반바지로도 가능하나 개인차 있음, 시작 시 조금 춥게 느껴질 수 있음"),

            (10, 15, 0, 100, 10, 20,
             "얇은 긴팔 티셔츠 + 바람막이 조끼", "롱 타이즈",
             "얇은 장갑, 버프, 헤드밴드",
             "강풍 시 체감온도 낮음 - 바람막이 필수"),

            # 7-10도 - 쌀쌀함 (장갑/조끼 시작 구간)
            (7, 10, 0, 100, 0, 10,
             "얇은 긴팔 티셔츠 (+ 런닝 조끼 선택)", "롱 타이즈",
             "얇은 손가락 장갑, 헤드밴드",
             "손이 시려울 수 있으므로 얇은 장갑 착용 권장. 조끼는 체온 조절에 유용함"),

            # 5-7도 - 추운 날씨 (보온 장갑/조끼 필수)
            (5, 7, 0, 100, 0, 10,
             "긴팔 티셔츠 + 런닝 조끼 또는 얇은 재킷", "롱 타이즈",
             "보온 장갑, 버프",
             "본격적으로 추운 날씨. 조끼를 활용하면 팔 움직임이 편하면서도 몸통 보온 가능"),

            (5, 10, 0, 100, 10, 20,
             "긴팔 티셔츠 + 방풍 재킷", "롱 타이즈",
             "보온 장갑, 버프, 귀마개",
             "강풍 시에는 조끼보다 방풍 재킷이 유리함"),

            # 0-5도 - 매우 추운 날씨
            (0, 5, 0, 100, 0, 10,
             "베이스레이어 + 긴팔 + 런닝 조끼 (또는 바람막이)", "기모 타이즈",
             "두꺼운 방한 장갑, 비니 또는 귀마개, 버프",
             "레이어링 필수. 조끼를 중간 레이어로 활용하면 보온성 증대"),

            (0, 5, 0, 100, 10, 20,
             "베이스레이어 + 중간층 + 방풍/방수 재킷", "기모 타이즈 + 방풍 팬츠",
             "두꺼운 방한 장갑, 비니, 넥워머, 버프",
             "강풍 시 매우 위험 - 체감온도 영하권, 충분한 워밍업 필요"),

            # 0도 이하 - 한겨울
            (-5, 0, 0, 100, 0, 10,
             "베이스레이어 + 플리스/조끼 + 방풍 재킷", "기모 타이즈 + 방풍 팬츠",
             "방한 장갑, 비니, 넥워머, 마스크 (선택)",
             "3겹 레이어링 권장. 조끼는 훌륭한 미들 레이어"),

            (-10, -5, 0, 100, 0, 15,
             "베이스레이어 + 플리스 + 방풍/방수 재킷 (3겹)", "기모 타이즈 + 방풍 팬츠",
             "방한 장갑 (이중 착용 고려), 비니, 넥워머, 마스크, 손난로",
             "빙판 주의, 짧은 거리 추천, 면 소재는 땀 배출이 안 되어 비추천"),

            # 습도 고려 추가 데이터
            (20, 25, 70, 100, 0, 10,
             "메쉬 또는 속건성 반팔 티셔츠", "러닝 반바지",
             "땀 흡수 헤드밴드, 선글라스",
             "고습도 - 땀 배출이 잘되는 기능성 소재 필수"),

            (10, 15, 70, 100, 0, 10,
             "속건성 긴팔 티셔츠 + 통풍 좋은 바람막이", "타이즈",
             "얇은 장갑",
             "습한 쌀쌀한 날씨 - 체온 유지와 통풍 모두 중요"),
        ]

        for data in sample_data:
            self.add_outfit(*data)
