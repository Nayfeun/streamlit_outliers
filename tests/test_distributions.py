import pandas as pd
import numpy as np

def test_df_col_names():
    distributions_df = pd.read_csv("src_data/distributions.csv", sep=";")
    assert distributions_df.columns[0] == "normal"

def test_mean():
    series = pd.Series([1, 2, 3])
    mean = np.mean(series)
    assert mean == 2