import os
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from distributions.distributions import get_outlier_amount, get_data_points, get_threshold, get_full_distribution
from distributions.models import Formula, Distribution


def get_user_distribution() -> Distribution:
    # User distribution and outliers shape
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


def get_user_csv(user_file):
    separator = st.selectbox('Values separator', options=[',', ';', r'\t'])
    user_df = pd.read_csv(user_file, sep=separator)
    values_col_names = st.radio("Click on the column where the values are", [column for column in user_df.columns])
    return user_df, values_col_names


def get_distribution_from_csv(user_csv: pd.DataFrame, values_col_name: str) -> pd.DataFrame:
    distribution = pd.DataFrame()
    distribution["Distribution"] = pd.Series(user_csv[values_col_name])
    distribution["Type"] = "Data points"
    return distribution


def formula_choice(custom: bool) -> Formula:
    user_formula = Formula()
    if not custom:
        outlier_method = st.radio("Method", ['2.5 MAD', '1.5 IQR', '2.5 SD', '3.0 SD'])
        if outlier_method.endswith('SD'):
            user_formula.sd_weight = 1
            user_formula.sd_constant = float(outlier_method[:3])
        elif outlier_method.endswith('MAD'):
            user_formula.mad_weight = 1
            user_formula.mad_constant = float(outlier_method[:3])
        else:
            user_formula.iqr_weight = 1
            user_formula.iqr_constant = 1.5

    else:
        user_formula.mad_weight, user_formula.iqr_weight, user_formula.sd_weight = [
            st.number_input(label=f'{method} weight (%)', min_value=0, max_value=100, step=1) / 100 for method in
            Formula.METHODS]

        user_formula.mad_constant, user_formula.iqr_constant, user_formula.sd_constant = [
            st.number_input(label=f'{method} constant', min_value=1.0, max_value=5.0, step=0.5) for method in
            Formula.METHODS]

    return user_formula


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


def distribution_graph(distribution, formula: Formula):
    # Set the background color and create a kernel density estimate plot without bars
    fig, ax = plt.subplots(figsize=(7, 5))

    # Create a KDE plot with different colors based on the "Type" column
    g = sns.kdeplot(data=distribution, x='Distribution', hue='Type', fill=True, common_norm=True, ax=ax, )

    # Set labels and title
    plt.xlabel('Value')
    plt.ylabel('Density')

    # Add vertical lines for threshold
    distribution_ndarray = distribution['Distribution'].__array__()
    threshold = get_threshold(distribution_ndarray, formula.mad_weight, formula.iqr_weight, formula.sd_weight,
                              formula.mad_constant,
                              formula.iqr_constant, formula.sd_constant)
    ax.axvline(x=threshold[0], color='red', linestyle='--', label='Line 1')
    ax.axvline(x=threshold[1], color='red', linestyle='--', label='Line 2')
    sns.move_legend(g, loc='upper right')

    st.write(fig)


def main():
    ### Config ###
    st.set_page_config(
        page_title="Outlier detection",
        layout="centered",
    )

    ### Tabs ###
    tab1, tab2 = st.tabs(['Simulation', 'Visualization'])

    with tab1:
        st.write("### Distribution")
        st.write("Choose the parameters of your distribution and outliers")
        user_distribution = get_user_distribution()
    with tab2:
        user_file = st.file_uploader("Import CSV", type='csv')
        if user_file is not None:
            user_csv, values_col_names = get_user_csv(user_file)

    # User formula selection
    st.write("### Formula")
    st.write("Choose the parameters of the outlier detection formula")
    custom = st.checkbox("Custom")
    user_formula = formula_choice(custom)
    if st.button("Run"):
        if user_file is None:
            user_full_distribution = simulate_distribution(user_distribution)
        else:
            user_full_distribution = get_distribution_from_csv(user_csv, values_col_names)
        distribution_graph(user_full_distribution, user_formula)


if __name__ == '__main__':
    main()
