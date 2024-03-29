import os
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from distributions.distributions import get_outlier_amount, get_data_points, get_threshold, get_full_distribution


def distribution_graph(distribution, w_mad, w_iqr, w_sd, const_mad, const_iqr, const_sd):
    # Set the background color and create a kernel density estimate plot without bars
    fig, ax = plt.subplots(figsize=(7, 5))

    # Create a KDE plot with different colors based on the "Type" column
    g = sns.kdeplot(data=distribution, x='Distribution', hue='Type', fill=True, common_norm=True, ax=ax, )

    # Set labels and title
    plt.xlabel('Value')
    plt.ylabel('Density')

    # Add vertical lines for threshold
    distribution_ndarray = distribution['Distribution'].__array__()
    threshold = get_threshold(distribution_ndarray, w_mad, w_iqr, w_sd, const_mad,
                              const_iqr, const_sd)
    ax.axvline(x=threshold[0], color='red', linestyle='--', label='Line 1')
    ax.axvline(x=threshold[1], color='red', linestyle='--', label='Line 2')
    sns.move_legend(g, loc='upper right')

    st.write(fig)


def guess_separator(file_path):
    possible_separators = [',', ';']  # Possible separators to check
    first_line = str(file_path.read().split()[0])
    for sep in possible_separators:
        if sep in first_line:
            st.write(f'{sep = }')
            return sep
    return r'\t'

def run():
    if user_file is None:
        user_full_distribution = get_full_distribution(distributions_df[user_distribution_shape.lower()],
                                                       user_distribution_size,
                                                       outliers_df[user_outliers_shape.lower().replace(" ", "_")],
                                                       user_outliers_rate)
    else:
        user_full_distribution = pd.DataFrame()
        user_full_distribution["Distribution"] = pd.Series(user_df[values])
        user_full_distribution["Type"] = "Data points"

    distribution_graph(user_full_distribution, user_mad_weight, user_iqr_weight, user_sd_weight, user_mad_constant,
                       user_iqr_constant, user_sd_constant)

# Config
st.set_page_config(
    page_title="Outlier detection",
    layout="centered",
)



# Sample distributions and outliers

file_path_distributions = os.path.join("src_data", "distributions.csv")
file_path_outliers = os.path.join("src_data", "outliers.csv")

distributions_df = pd.read_csv(file_path_distributions, sep=";", decimal=".")
outliers_df = pd.read_csv(file_path_outliers, sep=";", decimal=",")

# Define shape names for distributions and outliers
distributions_shapes = distributions_df.columns
outliers_shapes = outliers_df.columns

### Tabs ###
tab1, tab2 = st.tabs(['Simulation', 'Visualization'])

with tab1:
    # User distribution and outliers shape
    user_distribution_shape = st.radio("Pick a distribution shape : ",
                                       [distribution_shape.title() for distribution_shape in distributions_shapes])

    user_outliers_shape = st.radio("Pick an outliers shape: ",
                                   [outliers_shape.title().replace("_", " ") for outliers_shape in outliers_shapes])

    user_distribution_size = st.slider(label="Pick a distribution size", min_value=1, max_value=1000)
    user_outliers_rate = st.slider(label="Pick an outliers rate (%)", min_value=1, max_value=40) / 100

with tab2:
    user_file = st.file_uploader("Import CSV", type='csv')
    separator = st.selectbox('Values separator', options=[',', ';', r'\t'], )

    if user_file is not None:
        user_df = pd.read_csv(user_file, sep=separator)
        values = st.radio("Click on the column where the values are", [column for column in user_df.columns])

# User formula choice
st.write("## Formula")
st.write("Choose the parameters of the outlier detection formula")

custom = st.checkbox("Custom")

if not custom:
    outlier_method = st.radio("Method", ['MAD', 'SD', 'IQR'])
else:
    user_mad_weight = st.number_input(label="MAD weight (%)", min_value=0, max_value=100, step=1) / 100
    user_iqr_weight = st.number_input(label="IQR weight (%)", min_value=0, max_value=100, step=1) / 100
    user_sd_weight = st.number_input(label="SD weight (%)", min_value=0, max_value=100, step=1) / 100

    user_mad_constant = st.number_input(label="MAD constant", min_value=1.0, max_value=5.0, step=0.5)
    user_iqr_constant = st.number_input(label="IQR constant", min_value=1.0, max_value=5.0, step=0.5)
    user_sd_constant = st.number_input(label="SD constant", min_value=1.0, max_value=5.0, step=0.5)

run_button = st.button("Run", on_click=run)


