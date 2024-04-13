import numpy as np
import pandas as pd
import math
from distributions.models import Formula
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns


def get_mad(data):
    median = np.nanmedian(data)
    deviations = np.abs(data - median)
    mad = np.nanmedian(deviations)
    div = 1/np.nanpercentile(data, 75)
    return mad * div


def calculate_mad(data):
    """
    Calculate the Median Absolute Deviation (MAD) of a given distribution.
    :param data: Input data for which MAD is calculated.
    :return: mad (float): MAD of the input data.
    """
    median = np.nanmedian(data)
    deviations = np.abs(data - median)
    mad = np.nanmedian(deviations)
    return mad * 1.4826


def calculate_iqr(data: np.ndarray):
    """
    Calculate the Inter-Quartile-Range (IQR) of a given distribution.
    :param data: Input data for which IQR is calculated.
    :return: iqr (float):IQR of the input data.
    """
    q1 = np.nanpercentile(data, 25)
    q3 = np.nanpercentile(data, 75)
    iqr = q3 - q1
    return iqr


def calculate_sd(data):
    """
    Calculate the Standard Deviation (sd) of a given distribution
    :param data: Input data for which sd is calculated.
    :return: sd (float): Standard deviation of the input data.
    """
    mean_value = np.nanmean(data)
    squared_diff = [(x - mean_value) ** 2 for x in data]
    div = len(data) - 1
    variance = np.nansum(squared_diff) / div
    sd = math.sqrt(variance)
    return sd


def get_outlier_amount(initial_distribution_size, rate):
    """
    Calculate the amount of outliers needed in order to reach desired outliers' rate in a distribution.
    :param initial_distribution_size: Length of the initial distribution.
    :param rate: Desired outliers' rate in the new distribution.
    :return: outlier_amount (float): Amount of outliers needed to the reach desired rate.
    """
    if 1 >= rate >= 0:
        outlier_amount = rate * initial_distribution_size / (1 - rate)
        outlier_amount = round(outlier_amount)
        # If rate is not zero, returns at least 1 outlier
        if outlier_amount < 1 and rate != 0:
            outlier_amount = 1
        return outlier_amount
    else:
        raise ValueError(f"rate must be between 0 and 1. Given {rate = }")


"""
Distribution manipulation
"""


def get_threshold(data, weight_mad, weight_iqr, weight_sd, const_mad, const_iqr, const_sd):
    """
    Calculate outlier detection thresholds using a combination of MAD, IQR, and SD.
    :param data: The input data for which outlier thresholds are calculated.
    :param weight_mad: Weight for MAD component in the threshold calculation.
    :param weight_iqr: Weight for IQR component in the threshold calculation.
    :param weight_sd: Weight for SD component in the threshold calculation.
    :param const_mad: Constant multiplier for MAD component in the threshold calculation.
    :param const_iqr: Constant multiplier for IQR component in the threshold calculation.
    :param const_sd: Constant multiplier for SD component in the threshold calculation.
    :return: thresh_down (float): Lower outlier detection threshold.
    thresh_up (float): Upper outlier detection threshold.
    """
    mad = calculate_mad(data)
    #mad = get_mad(data)
    iqr = calculate_iqr(data)
    sd = calculate_sd(data)
    thresh_up = weight_mad * (np.nanmedian(data) + const_mad * mad) + weight_iqr * (
            np.nanpercentile(data, 75) + const_iqr * iqr) + weight_sd * (np.nanmean(data) + const_sd * sd)
    thresh_down = weight_mad * (np.nanmedian(data) - const_mad * mad) + weight_iqr * (
            np.nanpercentile(data, 25) - const_iqr * iqr) + weight_sd * (np.nanmean(data) - const_sd * sd)
    return thresh_down, thresh_up


def get_data_points(distribution, distribution_size, outliers, outliers_rate):
    """
    Define distribution array of desired size with desired outliers' rate.
    :param distribution: Input pandas Series containing the distribution.
    :param distribution_size: Desired number of data points from the initial distribution.
    :param outliers: Input pandas Series containing the outliers.
    :param outliers_rate: Desired rate of outliers in the final distribution.
    :return: Numpy array of the final distribution with outliers.
    """
    distribution = distribution.__array__()
    new_distribution = [distribution[x] for x in range(distribution_size)]
    outlier_amount = get_outlier_amount(distribution_size, outliers_rate)
    new_outliers = outliers.sample(frac=outlier_amount / len(outliers)).__array__()
    return np.concatenate([new_distribution, new_outliers])


def get_full_distribution(distribution, n_distribution: int, outliers: str, outliers_rate: float) -> pd.DataFrame:
    distribution_df = pd.DataFrame()
    distribution_df["Distribution"] = distribution.sample(frac=n_distribution/len(distribution))
    distribution_df["Type"] = "Valid data points"

    outliers_df = pd.DataFrame()
    outlier_amount = get_outlier_amount(n_distribution, outliers_rate)
    outliers_df["Distribution"] = outliers.sample(frac=outlier_amount/len(outliers))
    outliers_df["Type"] = "Outliers"
    return pd.concat([distribution_df, outliers_df])


def formula_choice() -> Formula:
    # User formula selection
    st.write("### Formula")
    st.write("Choose the parameters of the outlier detection formula")
    custom = st.checkbox("Custom")
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


def distribution_graph(distribution, formula: Formula):
    # Set the background color and create a kernel density estimate plot without bars
    fig, ax = plt.subplots(figsize=(7, 5))

    # Create a KDE plot with different colors based on the "Type" column
    try:
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
    except TypeError:
        st.error('The chosen column is not numeric. Please choose another column.')

