import streamlit as st
import pandas as pd
import numpy as np
from distributions.distributions import get_outlier_amount, get_data_points, threshold

#distributions_df = pd.read_csv("src_data\distributions.csv")
with open("src_data\distributions.csv") as distributions:
    distributions_shapes = distributions.readline().replace('"', "").replace('\n', "").split(";")

with open("src_data\outliers.csv") as outliers:
    outliers_shapes = outliers.readline().replace('"', "").replace('\n', "").replace('_', " ").split(";")

user_distribution_shape = st.sidebar.radio("Pick a distribution shape : ",
                                           [distribution_shape.title() for distribution_shape in distributions_shapes])

user_outliers_shape = st.sidebar.radio("Pick a distribution shape : ",
                                       [outliers_shape.title() for outliers_shape in outliers_shapes])

st.button("RUN", on_click=lambda: st.write(user_distribution_shape, user_outliers_shape))
