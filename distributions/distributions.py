import numpy as np
import pandas as pd
import math


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


def threshold(data, weight_mad, weight_iqr, weight_sd, const_mad, const_iqr, const_sd):
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
