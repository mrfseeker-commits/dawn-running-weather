import requests
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

def test_autocomplete():
    queries = ["목상동", "송강동", "용호동", "구성동", "강남역"]
    
    print(f"{'Query':<10} {'Result'}")
    print("-" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://weather.naver.com/'
    }

    for q in queries:
        url = f"https://ac.weather.naver.com/ac?q={q}&target=fa"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Structure is usually: {"items": [[["Name", "Code", ...]]]}
                if 'items' in data and data['items']:
                    items = data['items'][0]
                    for item in items:
                        # item is usually [name, code, ...]
                        name = item[0]
                        code = item[1]
                        print(f"{q:<10} {name} -> {code}")
                else:
                    print(f"{q:<10} No items found")
            else:
                print(f"{q:<10} Error {response.status_code}")
        except Exception as e:
            print(f"{q:<10} Failed {e}")

if __name__ == "__main__":
    test_autocomplete()
