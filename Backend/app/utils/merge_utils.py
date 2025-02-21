import pandas as pd

def merge_with_dedup(df1, df2, left_on, right_on, how='left', subset=None, suffixes=('_x', '_y')):
    """
    Reusable function to merge two DataFrames after removing duplicates based on a subset of columns.
    
    Parameters:
    df1 (pd.DataFrame): The first DataFrame 
    df2 (pd.DataFrame): The second DataFrame.
    left_on (str): Column name in df1 to merge on.
    right_on (str): Column name in df2 to merge on.
    how (str): Type of merge to be performed. Options: 'left', 'right', 'outer', 'inner'. Default is 'left'.
    subset (str or list): Column(s) in df2 on which to drop duplicates. Default is None (no duplicates dropped).
    suffixes (tuple): Suffixes to apply to overlapping column names in the DataFrames. Default is ('_x', '_y').
    
    Returns:
    pd.DataFrame: Merged DataFrame after dropping duplicates from df2.
    """
    
    if subset:
        df2 = df2.drop_duplicates(subset=subset, keep='first')
    
    merged_df = df1.merge(df2, left_on=left_on, right_on=right_on, how=how, suffixes=suffixes)
    
    return merged_df
