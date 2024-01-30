import pandas as pd


def test_df_col_names():
    distributions_df = pd.read_csv("src_data/distributions.csv", sep=";")
    assert distributions_df.columns[0] == "normal"

