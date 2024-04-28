import streamlit as st
import pandas as pd
from distributions.distributions import distribution_graph, formula_choice
from distributions.models import Formula


def get_distribution_from_df(user_df: pd.DataFrame, values_col_name: str) -> pd.DataFrame:
    distribution = pd.DataFrame()
    distribution["Distribution"] = pd.Series(user_df[values_col_name])
    distribution["Type"] = "Data points"
    return distribution


def run_visualization(df: pd.DataFrame, col_name: str, formula: Formula):
    user_full_distribution = get_distribution_from_df(df, col_name)
    fig_container = st.container(border=True)
    with fig_container:
        distribution_graph(fig_container, user_full_distribution, formula)


def main():
    user_file = st.file_uploader("Import CSV", type='csv')
    if user_file is not None:
        separator = st.selectbox('Values separator', options=[',', ';', r'\t'])

        try:
            user_df = pd.read_csv(user_file, sep=separator, engine='python')
            values_col_names = st.radio("Click on the column where the values are",
                                        [column for column in user_df.columns])

            user_formula = formula_choice()
            st.button('Run', on_click=run_visualization, kwargs={'df': user_df,
                                                                 'col_name': values_col_names,
                                                                 'formula': user_formula
                                                                 })
        except pd.errors.ParserError:
            st.error('Please select the right values separator')
        except:
            st.error('Something went wrong')


if __name__ == '__main__':
    main()
