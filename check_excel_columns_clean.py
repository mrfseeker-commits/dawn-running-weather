import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_columns():
    excel_path = '행정구역별_위경도_좌표.xlsx'
    try:
        df = pd.read_excel(excel_path, nrows=0) # Read header only
        print("Columns:")
        for col in df.columns:
            print(f"- {col}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_columns()
