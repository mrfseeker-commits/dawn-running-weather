import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_columns():
    excel_path = '행정구역별_위경도_좌표.xlsx'
    try:
        df = pd.read_excel(excel_path, nrows=5)
        print("Columns:", df.columns.tolist())
        print("First row:", df.iloc[0].to_dict())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_columns()
