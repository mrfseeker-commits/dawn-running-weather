"""
실시간 네이버 지역코드 검색 모듈
- 엑셀 파일의 위경도 정보를 활용
- API 키 없이 네이버 지역코드 조회
"""

import pandas as pd
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')


class RealtimeRegionCodeFinder:
    """엑셀 기반 실시간 지역코드 검색기"""

    def __init__(self, excel_path=None):
        """
        Args:
            excel_path: 행정구역별 위경도 엑셀 파일 경로
        """
        if excel_path is None:
            import os
            # 현재 스크립트 디렉토리에서 엑셀 파일 찾기
            script_dir = os.path.dirname(os.path.abspath(__file__))
            excel_path = os.path.join(script_dir, '행정구역별_위경도_좌표.xlsx')

        self.excel_path = excel_path
        self.df = None
        self.load_excel()

    def load_excel(self):
        """엑셀 파일 로드 - 모든 시트를 통합"""
        try:
            xl_file = pd.ExcelFile(self.excel_path)
            all_dfs = []

            for sheet_name in xl_file.sheet_names:
                df_sheet = pd.read_excel(xl_file, sheet_name=sheet_name)
                all_dfs.append(df_sheet)

            # 모든 시트를 하나의 DataFrame으로 통합
            self.df = pd.concat(all_dfs, ignore_index=True)
            print(f"✓ 엑셀 파일 로드 완료: {len(xl_file.sheet_names)}개 시트, {len(self.df)}개 행정구역")

        except FileNotFoundError:
            print(f"✗ 엑셀 파일을 찾을 수 없습니다: {self.excel_path}")
            self.df = pd.DataFrame()
        except Exception as e:
            print(f"✗ 엑셀 파일 로드 실패: {e}")
            self.df = pd.DataFrame()

    def normalize_keyword(self, keyword):
        """
        검색 키워드 정규화
        - "서울" → "서울특별시"
        - "대전" → "대전광역시"
        """
        replacements = {
            '서울': '서울특별시',
            '부산': '부산광역시',
            '대구': '대구광역시',
            '인천': '인천광역시',
            '광주': '광주광역시',
            '대전': '대전광역시',
            '울산': '울산광역시',
            '세종': '세종특별자치시',
            '제주': '제주특별자치도'
        }

        for short, full in replacements.items():
            # 단어 경계에서만 치환 (예: "서울" → "서울특별시", but "서울시" → "서울특별시시" 방지)
            if keyword.startswith(short + ' ') or keyword == short:
                keyword = keyword.replace(short, full, 1)
                break

        return keyword

    def search_address(self, keyword):
        """
        키워드로 행정구역 검색

        Args:
            keyword: 검색 키워드 (예: "대전 유성구", "송강동")

        Returns:
            list: 검색 결과 리스트 [{'full_name': str, 'lat': float, 'lng': float}, ...]
        """
        if self.df is None or self.df.empty:
            return []

        # 키워드 정규화
        normalized_keyword = self.normalize_keyword(keyword)

        results = []

        for idx, row in self.df.iterrows():
            # NaN 값 처리
            sido = str(row['시도']) if pd.notna(row['시도']) else ''
            sigungu = str(row['시군구']) if pd.notna(row['시군구']) else ''
            eupmyeondong = str(row['읍면동/구']) if pd.notna(row['읍면동/구']) else ''

            # 전체 주소 생성
            parts = [p for p in [sido, sigungu, eupmyeondong] if p]
            full_name = ' '.join(parts)

            # 키워드 매칭 (대소문자 무시, 공백 무시)
            keyword_norm = normalized_keyword.replace(' ', '').lower()
            fullname_norm = full_name.replace(' ', '').lower()

            if keyword_norm in fullname_norm:
                results.append({
                    'full_name': full_name,
                    'lat': row['위도'],
                    'lng': row['경도'],
                    'sido': sido,
                    'sigungu': sigungu,
                    'eupmyeondong': eupmyeondong
                })

        return results

    def get_region_code(self, keyword, lat=None, lng=None, delay=0.1):
        """
        지역명으로 네이버 지역코드 조회 (Playwright 사용)
        
        Args:
            keyword: 지역명 (예: "대전 목상동")
            lat, lng: (사용 안 함, 호환성 위해 유지)
            delay: (사용 안 함)

        Returns:
            str: 네이버 지역코드 (예: "07230112") 또는 None
        """
        from playwright.sync_api import sync_playwright
        import time

        print(f"지역 코드 검색 (Playwright): {keyword}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                try:
                    # 네이버 날씨 홈 이동
                    page.goto("https://weather.naver.com/", wait_until='domcontentloaded', timeout=15000)
                    
                    # 검색창 찾기 (버튼 뒤에 숨겨져 있을 수 있음)
                    try:
                        page.wait_for_selector("input.interest_form_input", state="attached", timeout=3000)
                        if not page.is_visible("input.interest_form_input"):
                            search_btn = page.query_selector("button[class*='search'], .btn_search, .button_search")
                            if search_btn:
                                search_btn.click()
                                page.wait_for_selector("input.interest_form_input", state="visible", timeout=3000)
                    except:
                        pass

                    # 검색어 입력
                    page.fill("input.interest_form_input", keyword)
                    
                    # 자동완성 결과 대기
                    page.wait_for_selector("a.interest_item_link", timeout=5000)
                    
                    # 첫 번째 결과 클릭
                    page.click("a.interest_item_link >> nth=0")
                    
                    # URL 변경 대기 (지역 코드가 포함된 URL로 이동)
                    page.wait_for_url("**/today/*", timeout=10000)
                    
                    current_url = page.url
                    if "/today/" in current_url:
                        code = current_url.split("/today/")[1].split("?")[0]
                        print(f"✓ 코드 발견: {code}")
                        return code
                        
                except Exception as e:
                    print(f"✗ Playwright 검색 실패: {e}")
                finally:
                    browser.close()

            return None

        except Exception as e:
            print(f"✗ 오류 발생: {e}")
            return None

    def get_weather_url(self, keyword, max_results=10, delay=0.2):
        """
        키워드로 날씨 URL 조회 (원스톱)

        Args:
            keyword: 지역 검색 키워드
            max_results: 최대 API 호출 개수 (너무 많은 요청 방지)
            delay: API 호출 간 대기 시간 (초)

        Returns:
            list: [{'name': str, 'url': str, 'code': str}, ...] 또는 빈 리스트
        """
        # 1. 주소 검색
        addresses = self.search_address(keyword)

        if not addresses:
            print(f"✗ '{keyword}' 검색 결과가 없습니다.")
            return []

        # 너무 많은 결과가 있으면 경고
        if len(addresses) > max_results:
            print(f"⚠ 검색 결과 {len(addresses)}개 중 처음 {max_results}개만 조회합니다.")
            addresses = addresses[:max_results]

        results = []

        # 2. 각 주소마다 지역코드 조회
        for addr in addresses:
            lat = addr['lat']
            lng = addr['lng']
            full_name = addr['full_name']

            # 3. 네이버 지역코드 조회
            region_code = self.get_region_code(lat, lng, delay=delay)

            if region_code:
                weather_url = f"https://weather.naver.com/today/{region_code}"
                results.append({
                    'name': full_name,
                    'url': weather_url,
                    'code': region_code,
                    'lat': lat,
                    'lng': lng
                })
                print(f"✓ {full_name} → {region_code}")
            else:
                print(f"✗ {full_name} → 지역코드 조회 실패")

        return results


def main():
    """사용 예시"""
    finder = RealtimeRegionCodeFinder()

    # 테스트 검색
    test_keywords = [
        "대전 유성구 송강동",
        "대전 대덕구 목상동",
        "서울 강남구"
    ]

    print("\n" + "="*80)
    print("실시간 네이버 지역코드 검색 테스트")
    print("="*80 + "\n")

    for keyword in test_keywords:
        print(f"\n🔍 검색: '{keyword}'")
        print("-" * 60)

        results = finder.get_weather_url(keyword)

        if results:
            print(f"\n총 {len(results)}개 결과:")
            for i, r in enumerate(results, 1):
                print(f"  {i}. {r['name']}")
                print(f"     코드: {r['code']}")
                print(f"     URL: {r['url']}")
                print(f"     위경도: ({r['lat']}, {r['lng']})")
        else:
            print("검색 결과 없음")

        print()


if __name__ == "__main__":
    main()
