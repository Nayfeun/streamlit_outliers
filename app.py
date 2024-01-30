import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from distributions.distributions import get_outlier_amount, get_data_points, threshold, get_full_distribution


def distribution_graph(distribution):
    # Set the background color and create a kernel density estimate plot without bars
    fig, ax = plt.subplots(figsize=(7, 5))

    # Create a KDE plot with different colors based on the "Type" column
    sns.kdeplot(data=distribution, x='Distribution', hue='Type', fill=True, common_norm=True,
                hue_order=["Valid data points", "Outliers"], ax=ax)  # Keep common_norm True

    # Set labels and title
    plt.xlabel('Value')
    plt.ylabel('Density')
    st.write(fig)


def run_button():
    user_full_distribution = get_full_distribution(distributions_df[user_distribution_shape.lower()], 1000, outliers_df[user_outliers_shape.lower().replace(" ", "_")], 0.4)
    distribution_graph(user_full_distribution)


distributions_df = pd.read_csv("src_data\distributions.csv", sep=";", decimal=".")
outliers_df = pd.read_csv("src_data\outliers.csv", sep=";", decimal=",")

distributions_shapes = distributions_df.columns
outliers_shapes = outliers_df.columns

user_distribution_shape = st.sidebar.radio("Pick a distribution shape : ",
                                           [distribution_shape.title() for distribution_shape in distributions_shapes])

user_outliers_shape = st.sidebar.radio("Pick an outliers shape: ",
                                       [outliers_shape.title().replace("_", " ") for outliers_shape in outliers_shapes])


st.button("RUN", on_click=run_button)



