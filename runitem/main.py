from database import RunningOutfitDB

def print_header():
    print("\n" + "="*60)
    print("     런닝 복장 추천 시스템")
    print("="*60)

def print_menu():
    print("\n메뉴:")
    print("1. 복장 추천 받기")
    print("2. 모든 복장 데이터 보기")
    print("3. 새로운 복장 데이터 추가")
    print("4. 복장 데이터 삭제")
    print("5. 샘플 데이터 초기화")
    print("0. 종료")
    print("-"*60)

def get_recommendation(db: RunningOutfitDB):
    print("\n[ 복장 추천 ]")
    try:
        temperature = float(input("기온(°C): "))

        humidity_input = input("습도(%) [Enter로 건너뛰기]: ").strip()
        humidity = float(humidity_input) if humidity_input else None

        wind_speed_input = input("풍속(m/s) [Enter로 건너뛰기]: ").strip()
        wind_speed = float(wind_speed_input) if wind_speed_input else None

        results = db.get_recommendation(temperature, humidity, wind_speed)

        if not results:
            print("\n해당 조건에 맞는 복장 추천이 없습니다.")
            return

        print("\n" + "="*60)
        print("추천 복장:")
        print("="*60)

        for idx, result in enumerate(results, 1):
            top, bottom, accessories, notes, temp_min, temp_max = result
            print(f"\n[ 추천 {idx} ] (적용 온도: {temp_min}°C ~ {temp_max}°C)")
            print(f"상의: {top}")
            print(f"하의: {bottom}")
            if accessories:
                print(f"액세서리: {accessories}")
            if notes:
                print(f"참고사항: {notes}")
            print("-"*60)

    except ValueError:
        print("올바른 숫자를 입력해주세요.")

def view_all_outfits(db: RunningOutfitDB):
    print("\n[ 모든 복장 데이터 ]")
    outfits = db.get_all_outfits()

    if not outfits:
        print("저장된 복장 데이터가 없습니다.")
        return

    for outfit in outfits:
        id_, temp_min, temp_max, hum_min, hum_max, wind_min, wind_max, top, bottom, acc, notes = outfit
        print(f"\nID: {id_}")
        print(f"온도 범위: {temp_min}°C ~ {temp_max}°C")
        if hum_min is not None or hum_max is not None:
            print(f"습도 범위: {hum_min}% ~ {hum_max}%")
        if wind_min is not None or wind_max is not None:
            print(f"풍속 범위: {wind_min}m/s ~ {wind_max}m/s")
        print(f"상의: {top}")
        print(f"하의: {bottom}")
        if acc:
            print(f"액세서리: {acc}")
        if notes:
            print(f"참고사항: {notes}")
        print("-"*60)

def add_outfit(db: RunningOutfitDB):
    print("\n[ 새로운 복장 데이터 추가 ]")
    try:
        temp_min = float(input("최저 온도(°C): "))
        temp_max = float(input("최고 온도(°C): "))

        hum_min_input = input("최저 습도(%) [Enter로 건너뛰기]: ").strip()
        hum_min = float(hum_min_input) if hum_min_input else None

        hum_max_input = input("최고 습도(%) [Enter로 건너뛰기]: ").strip()
        hum_max = float(hum_max_input) if hum_max_input else None

        wind_min_input = input("최저 풍속(m/s) [Enter로 건너뛰기]: ").strip()
        wind_min = float(wind_min_input) if wind_min_input else None

        wind_max_input = input("최고 풍속(m/s) [Enter로 건너뛰기]: ").strip()
        wind_max = float(wind_max_input) if wind_max_input else None

        top = input("상의: ")
        bottom = input("하의: ")
        accessories = input("액세서리 [Enter로 건너뛰기]: ")
        notes = input("참고사항 [Enter로 건너뛰기]: ")

        db.add_outfit(temp_min, temp_max, hum_min, hum_max, wind_min, wind_max,
                     top, bottom, accessories, notes)
        print("\n복장 데이터가 추가되었습니다!")

    except ValueError:
        print("올바른 값을 입력해주세요.")

def delete_outfit(db: RunningOutfitDB):
    print("\n[ 복장 데이터 삭제 ]")
    view_all_outfits(db)

    try:
        outfit_id = int(input("\n삭제할 데이터의 ID: "))
        confirm = input(f"ID {outfit_id}를 삭제하시겠습니까? (y/n): ")

        if confirm.lower() == 'y':
            db.delete_outfit(outfit_id)
            print("삭제되었습니다.")
        else:
            print("취소되었습니다.")

    except ValueError:
        print("올바른 ID를 입력해주세요.")

def initialize_data(db: RunningOutfitDB):
    confirm = input("기존 데이터를 모두 삭제하고 샘플 데이터로 초기화하시겠습니까? (y/n): ")

    if confirm.lower() == 'y':
        # 기존 데이터 삭제
        db.cursor.execute('DELETE FROM outfit_recommendations')
        db.conn.commit()

        # 샘플 데이터 추가
        db.initialize_sample_data()
        print("샘플 데이터로 초기화되었습니다!")
    else:
        print("취소되었습니다.")

def main():
    db = RunningOutfitDB()
    db.connect()
    db.create_tables()

    # 데이터베이스가 비어있으면 샘플 데이터 자동 추가
    if not db.get_all_outfits():
        print("데이터베이스가 비어있습니다. 샘플 데이터를 추가합니다...")
        db.initialize_sample_data()
        print("샘플 데이터가 추가되었습니다!")

    print_header()

    try:
        while True:
            print_menu()
            choice = input("선택: ").strip()

            if choice == '1':
                get_recommendation(db)
            elif choice == '2':
                view_all_outfits(db)
            elif choice == '3':
                add_outfit(db)
            elif choice == '4':
                delete_outfit(db)
            elif choice == '5':
                initialize_data(db)
            elif choice == '0':
                print("\n프로그램을 종료합니다.")
                break
            else:
                print("\n올바른 메뉴를 선택해주세요.")

    finally:
        db.close()

if __name__ == "__main__":
    main()
