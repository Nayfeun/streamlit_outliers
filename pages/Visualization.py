import streamlit as st
import pandas as pd
from distributions.distributions import distribution_graph, formula_choice, get_plot_kind
from distributions.models import Formula


def get_distribution_from_df(user_df: pd.DataFrame, values_col_name: str) -> pd.DataFrame:
    distribution = pd.DataFrame()
    distribution["Distribution"] = pd.Series(user_df[values_col_name])
    distribution["Type"] = "Data points"
    return distribution


def run_visualization(df: pd.DataFrame, col_name: str, formula: Formula, kind: str):
    user_full_distribution = get_distribution_from_df(df, col_name)
    distribution_graph(distribution=user_full_distribution, formula=formula, kind=kind)


def main():
    #Layout
    st.set_page_config(page_title='Visualization - Outlier Detection')

    user_file = st.file_uploader("Import CSV", type='csv')
    user_formula = formula_choice()
    plot_kind = get_plot_kind()

    if user_file is not None:
        separator = st.selectbox('Values separator', options=[',', ';', r'\t'])

        try:
            user_df = pd.read_csv(user_file, sep=separator, engine='python')
            values_col_names = st.radio("Click on the column where the values are",
                                        [column for column in user_df.columns])

            st.button('View', on_click=run_visualization, kwargs={'df': user_df,
                                                                 'col_name': values_col_names,
                                                                 'formula': user_formula,
                                                                  'kind': plot_kind
                                                                 })
        except pd.errors.ParserError:
            st.error('Please select the right values separator')
        except:
            st.error('Something went wrong')


if __name__ == '__main__':
    main()
