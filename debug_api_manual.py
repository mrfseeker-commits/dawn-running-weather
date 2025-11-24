import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_api():
    # Test cases: (Name, Lat, Lng)
    test_cases = [
        ("대전 목상동", 36.4485001, 127.4122517),
        ("대전 송강동", 36.429926, 127.381663),
        ("대전 용호동", 36.4350346, 127.449175),
        ("대전 구성동", 36.370724, 127.3661),
        ("서울 강남역", 37.4979, 127.0276) # Control
    ]

    print(f"{'Region':<15} {'Lat':<10} {'Lng':<10} {'Result Code'}")
    print("-" * 60)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://weather.naver.com/'
    }

    for name, lat, lng in test_cases:
        url = f"https://weather.naver.com/api/naverRgnCatForCoords?lat={lat}&lng={lng}"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                code = data.get('regionCode', 'No Code')
                print(f"{name:<15} {lat:<10.4f} {lng:<10.4f} {code}")
                # print(f"  Full Response: {data}") 
            else:
                print(f"{name:<15} {lat:<10.4f} {lng:<10.4f} Error {response.status_code}")
        except Exception as e:
            print(f"{name:<15} {lat:<10.4f} {lng:<10.4f} Failed {e}")

if __name__ == "__main__":
    test_api()
