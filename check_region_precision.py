import pandas as pd
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_coordinates_and_api():
    excel_path = '행정구역별_위경도_좌표.xlsx'
    
    # Target regions to check
    targets = ["목상동", "송강동", "용호동", "구성동"]
    
    print(f"Loading Excel: {excel_path}")
    try:
        xl_file = pd.ExcelFile(excel_path)
        all_dfs = []
        for sheet_name in xl_file.sheet_names:
            df_sheet = pd.read_excel(xl_file, sheet_name=sheet_name)
            all_dfs.append(df_sheet)
        df = pd.concat(all_dfs, ignore_index=True)
    except Exception as e:
        print(f"Failed to load Excel: {e}")
        return

    print("\nChecking coordinates in Excel:")
    found_coords = []
    
    for target in targets:
        # Filter for the target dong
        # Assuming column names based on previous knowledge or standard format
        # Usually '읍면동/구' or similar. Let's search in all string columns
        
        # Simple search in '읍면동/구' if it exists, otherwise search all
        mask = df.apply(lambda row: row.astype(str).str.contains(target).any(), axis=1)
        results = df[mask]
        
        if not results.empty:
            for _, row in results.iterrows():
                # Construct full name
                sido = str(row.get('시도', ''))
                sigungu = str(row.get('시군구', ''))
                dong = str(row.get('읍면동/구', ''))
                full_name = f"{sido} {sigungu} {dong}".strip()
                
                if '대전' not in full_name: # Filter for Daejeon as per user context
                    continue
                    
                lat = row.get('위도')
                lng = row.get('경도')
                
                print(f"Found: {full_name} -> Lat: {lat}, Lng: {lng}")
                found_coords.append((full_name, lat, lng))
        else:
            print(f"Not found in Excel: {target}")

    print("\nTesting Naver API for found coordinates:")
    for name, lat, lng in found_coords:
        url = f"https://weather.naver.com/api/naverRgnCatForCoords?lat={lat}&lng={lng}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"{name} FULL RESPONSE: {data}")
            else:
                print(f"{name}: API Error {response.status_code}")
        except Exception as e:
            print(f"{name}: Request Failed {e}")

if __name__ == "__main__":
    check_coordinates_and_api()
