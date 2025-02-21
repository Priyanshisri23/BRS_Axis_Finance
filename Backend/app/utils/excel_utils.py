import pandas as pd

def get_excel_data(file_path, sheet_name='Sheet1'):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    # df to dict
    result_dict = pd.Series(df.iloc[:, 1].values, index=df.iloc[:, 0]).to_dict()
    return result_dict
