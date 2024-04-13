from distributions.models import Distribution
from distributions.distributions import get_full_distribution, distribution_graph, formula_choice
import streamlit as st
import pandas as pd
import os


def get_user_distribution() -> Distribution:
    # User distribution and outliers shape
    st.write("### Distribution")
    st.write("Choose the parameters of your distribution and outliers")

    user_distribution = Distribution()
    user_distribution.distribution_shape = st.radio("Distribution shape : ",
                                                    [distribution_shape.title() for distribution_shape in
                                                     Distribution.DISTRIBUTION_SHAPES])
    user_distribution.outliers_shape = st.radio("Outliers shape: ",
                                                [outliers_shape.title().replace("_", " ") for outliers_shape in
                                                 Distribution.OUTLIERS_SHAPES])
    user_distribution.distribution_size = st.slider(label="Distribution size", min_value=1, max_value=1000)
    user_distribution.outliers_rate = st.slider(label="Outliers rate (%)", min_value=1, max_value=40) / 100
    return user_distribution


def simulate_distribution(user_distribution: Distribution) -> pd.DataFrame:
    file_path_distributions = os.path.join("data", "distributions.csv")
    file_path_outliers = os.path.join("data", "outliers.csv")

    distributions_df = pd.read_csv(file_path_distributions, sep=";", decimal=".")
    outliers_df = pd.read_csv(file_path_outliers, sep=";", decimal=",")

    distribution = get_full_distribution(distributions_df[user_distribution.distribution_shape.lower()],
                                         user_distribution.distribution_size,
                                         outliers_df[
                                             user_distribution.outliers_shape.lower().replace(" ", "_")],
                                         user_distribution.outliers_rate)
    return distribution


def run_simulation(distribution, formula):
    user_full_distribution = simulate_distribution(distribution)
    distribution_graph(user_full_distribution, formula)


def main():
    user_distribution = get_user_distribution()
    user_formula = formula_choice()
    st.button('Run', on_click=run_simulation, kwargs={'distribution': user_distribution, 'formula': user_formula})


if __name__ == '__main__':
    main()
