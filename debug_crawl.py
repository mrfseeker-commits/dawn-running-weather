from weather_service import crawl_weather
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def test():
    region_code = "07200580" # Jagok-dong
    url = f"https://weather.naver.com/today/{region_code}"
    
    print(f"Testing crawl for {url}...")
    try:
        data = crawl_weather(url, region_code)
        print(f"Crawl result count: {len(data)}")
        if data:
            print("First 3 entries:")
            for item in data[:3]:
                print(item)
        else:
            print("No data returned.")
    except Exception as e:
        print(f"Crawl failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
