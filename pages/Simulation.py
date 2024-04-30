from distributions.models import Distribution, Formula
from distributions.distributions import get_full_distribution, distribution_graph, formula_choice, get_plot_kind
import streamlit as st
import pandas as pd
import os


def get_user_distribution(container_1: st.container, container_2: st.container) -> Distribution:
    # User distribution parameters selection
    with container_1:
        st.subheader("Distribution parameters")

        user_distribution = Distribution()
        user_distribution.distribution_shape = st.radio("Shape : ",
                                                        [distribution_shape.title() for distribution_shape in
                                                         Distribution.DISTRIBUTION_SHAPES])
        user_distribution.distribution_size = st.slider(label="Distribution size", min_value=10, max_value=1000,
                                                        value=100)
    # User outliers parameters selection
    with container_2:
        st.subheader("Outlier distribution parameters")

        user_distribution.outliers_shape = get_outliers_shape()
        user_distribution.outliers_rate = st.slider(label="Outliers rate (%)", min_value=1, max_value=40,
                                                    value=10) / 100
    return user_distribution


def get_outliers_shape() -> str:
    col_1, col_2 = st.columns(2)
    with col_1:
        spread = st.radio(label='Spread : ', options=['Centered', 'Dispersed'],
                          help='Width of the outlier distribution')
        distance = st.radio(label='Distance : ', options=['Close', 'Extreme'], help='How far the outlier distribution '
                                                                                    'is from the distribution')
    with col_2:
        sides = st.radio(label='Sides : ', options=['1 side', '2 side'],
                         help='Choose if the outliers should be on the right side of the distribution, or also on the left side.')
        outliers_shape = f'outlier_{sides[0]}_side_{spread.lower()}_{distance.lower()}'
    if outliers_shape in Distribution.OUTLIERS_SHAPES:
        return outliers_shape
    else:
        raise ValueError('Incorrect outliers shape')


def simulate_distribution(user_distribution: Distribution) -> pd.DataFrame:
    # Get path of sample data csv and import them
    file_path_distributions = os.path.join("data", "distributions.csv")
    file_path_outliers = os.path.join("data", "outliers.csv")

    distributions_df = pd.read_csv(file_path_distributions, sep=";", decimal=".")
    outliers_df = pd.read_csv(file_path_outliers, sep=";", decimal=",")

    # Import distribution from users chosen parameters
    distribution = get_full_distribution(distributions_df[user_distribution.distribution_shape.lower()],
                                         user_distribution.distribution_size,
                                         outliers_df[
                                             user_distribution.outliers_shape.lower().replace(" ", "_")],
                                         user_distribution.outliers_rate)
    return distribution


def run_simulation(distribution: Distribution, formula: Formula, kind: str):
    # Import Data from sample csv
    distribution.data = simulate_distribution(distribution)
    # Make a plot of the data
    distribution_graph(distribution=distribution.data, formula=formula, kind=kind)


def main():
    # Layout
    st.set_page_config(layout='wide',
                       page_title='Simulation - Outlier Detection')
    col_1, col_2, = st.columns(2, gap='medium')

    # Allow user to choose distribution and outliers parameters
    user_distribution = get_user_distribution(col_1, col_2)

    # Allow user to select formula and figure kind in sidebar
    user_formula = formula_choice()
    plot_kind = get_plot_kind()

    # Create button to view the figure
    st.button('View', on_click=run_simulation,
              kwargs={'distribution': user_distribution, 'formula': user_formula, 'kind': plot_kind})


if __name__ == '__main__':
    main()
