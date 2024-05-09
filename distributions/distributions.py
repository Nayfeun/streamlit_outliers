import numpy as np
import pandas as pd
import math
from distributions.models import Formula
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm


def get_mad(data: np.ndarray) -> float:
    """
    Calculate adjusted Median Absolute Deviation (MAD) of a given distribution.
    :param data: Input data for which adjusted MAD is calculated.
    :return: Adjusted MAD of the input data.
    """
    median_value = np.median(data)
    absolute_deviations = np.abs(data - median_value)
    mad_value = np.median(absolute_deviations)
    scale_factor = 1 / norm.ppf(3/4)  # Quantile function at 75th percentile
    scaled_mad = mad_value * scale_factor

    return scaled_mad


def calculate_mad(data: np.ndarray) -> float:
    """
    Calculate the Median Absolute Deviation (MAD) of a given distribution.
    :param data: Input data for which MAD is calculated.
    :return: MAD of the input data.
    """
    median = np.nanmedian(data)
    deviations = np.abs(data - median)
    mad = np.nanmedian(deviations)
    return mad * 1.4826


def calculate_iqr(data: np.ndarray) -> float:
    """
    Calculate the Inter-Quartile-Range (IQR) of a given distribution.
    :param data: Input data for which IQR is calculated.
    :return: IQR of the input data.
    """
    q1 = np.nanpercentile(data, 25)
    q3 = np.nanpercentile(data, 75)
    iqr = q3 - q1
    return iqr


def calculate_sd(data: np.ndarray) -> float:
    """
    Calculate the Standard Deviation (sd) of a given distribution
    :param data: Input data for which sd is calculated.
    :return: sd: Standard deviation of the input data.
    """
    mean_value = np.nanmean(data)
    squared_diff = [(x - mean_value) ** 2 for x in data]
    div = len(data) - 1
    variance = np.nansum(squared_diff) / div
    sd = math.sqrt(variance)
    return sd


def get_outlier_amount(initial_distribution_size: int, rate: float) -> float:
    """
    Calculate the amount of outliers needed in order to reach desired outliers' rate in a distribution.
    :param initial_distribution_size: Length of the initial distribution.
    :param rate: Desired outliers' rate in the new distribution.
    :return: Amount of outliers needed to the reach desired rate.
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


def get_threshold(data: np.ndarray, weight_mad: float, weight_iqr: float, weight_sd: float, weight_adjusted_mad: float,
                  const_mad: float,
                  const_iqr: float, const_sd: float, const_adjusted_mad: float) -> float:
    """
    Calculate outlier detection thresholds using a combination of MAD, IQR, and SD.
    :param data: The input data for which outlier thresholds are calculated.
    :param weight_mad: Weight for MAD component in the threshold calculation.
    :param weight_iqr: Weight for IQR component in the threshold calculation.
    :param weight_sd: Weight for SD component in the threshold calculation.
    :param weight_adjusted_mad: Weight for adjusted MAD component in the threshold calculation.
    :param const_mad: Constant multiplier for MAD component in the threshold calculation.
    :param const_iqr: Constant multiplier for IQR component in the threshold calculation.
    :param const_sd: Constant multiplier for SD component in the threshold calculation.
    :param const_adjusted_mad: Constant multiplier for adjusted MAD component in the threshold calculation.
    :return: thresh_down (float): Lower outlier detection threshold.
    thresh_up (float): Upper outlier detection threshold.
    """
    mad = calculate_mad(data)
    iqr = calculate_iqr(data)
    sd = calculate_sd(data)
    adjusted_mad = get_mad(data)
    thresh_up = weight_adjusted_mad * (np.nanmedian(data) + const_adjusted_mad * adjusted_mad) + weight_mad * (
                np.nanmedian(data) + const_mad * mad) + weight_iqr * (
                        np.nanpercentile(data, 75) + const_iqr * iqr) + weight_sd * (np.nanmean(data) + const_sd * sd)
    thresh_down = weight_adjusted_mad * (np.nanmedian(data) - const_adjusted_mad * adjusted_mad) + weight_mad * (
                np.nanmedian(data) - const_mad * mad) + weight_iqr * (
                          np.nanpercentile(data, 25) - const_iqr * iqr) + weight_sd * (np.nanmean(data) - const_sd * sd)
    return thresh_down, thresh_up


def get_data_points(distribution: np.ndarray, distribution_size: int, outliers: np.ndarray,
                    outliers_rate: float) -> np.ndarray:
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


def get_full_distribution(distribution: pd.Series, n_distribution: int, outliers: str,
                          outliers_rate: float) -> pd.DataFrame:
    """
    Get Dataframe of distribution with outliers from desired length, outliers kind, and outliers rate.
    :param distribution: Series with distribution values
    :param n_distribution: Length of the distribution
    :param outliers: Type of outliers to be added to the initial distribution
    :param outliers_rate: Rate of outliers to be added to the initial distribution
    :return: Dataframe with column 'Distribution' including values of distribution and outliers, and column 'Type' indicating if
    each datapoint is a valid data point or an outlier.
    """
    distribution_df = pd.DataFrame()
    distribution_df["Distribution"] = distribution.sample(frac=n_distribution / len(distribution))
    distribution_df["Type"] = "Valid data points"

    outliers_df = pd.DataFrame()
    outlier_amount = get_outlier_amount(n_distribution, outliers_rate)
    outliers_df["Distribution"] = outliers.sample(frac=outlier_amount / len(outliers))
    outliers_df["Type"] = "Outliers"
    return pd.concat([distribution_df, outliers_df])


def formula_choice() -> Formula:
    """
    Allow user to select a formula from sidebar on a streamlit app.
    :return: Desired formula.
    """
    # User formula selection
    with st.sidebar:
        st.subheader("Choose the parameters of the outlier detection formula")
        custom = st.checkbox("Custom")
        user_formula = Formula()

        if not custom:
            outlier_method = st.radio("Method", ['2.5 MAD', '2.5 Adjusted MAD', '1.5 IQR', '2.5 SD', '3.0 SD'])
            if outlier_method.endswith('SD'):
                user_formula.sd_weight = 1
                user_formula.sd_constant = float(outlier_method[:3])
            elif outlier_method == '2.5 MAD':
                user_formula.mad_weight = 1
                user_formula.mad_constant = float(outlier_method[:3])
            elif outlier_method.endswith('Adjusted MAD'):
                user_formula.adjusted_mad_weight = 1
                user_formula.adjusted_mad_constant = float(outlier_method[:3])
            else:
                user_formula.iqr_weight = 1
                user_formula.iqr_constant = 1.5

        else:
            user_formula.mad_weight, user_formula.iqr_weight, user_formula.sd_weight, user_formula.adjusted_mad_weight = [
                st.number_input(label=f'{method} weight (%)', min_value=0, max_value=100, step=1) / 100 for method in
                Formula.METHODS]

            user_formula.mad_constant, user_formula.iqr_constant, user_formula.sd_constant, user_formula.adjusted_mad_constant = [
                st.number_input(label=f'{method} constant', min_value=1.0, max_value=5.0, step=0.5) for method in
                Formula.METHODS]
        # Explanations
        expander = st.expander('See explanation')
        expander.write(
            """
            The formulas shown above are the most used univariate outlier detection formulas.
            Each formula calculates a threshold, outside of which each data point will be considered as an outlier. The 
            resulting threshold is indicated in the figure by two vertical lines.
            
            By clicking Custom, you can further 
            modify the formula parameters. You can combine formulas by changing each formula's weight and constant. 
            The resulting threshold will be the weighted mean of each formula's output.
            
            ## Methods 
            
            1. **MAD** Median Absolute Deviation
            
            *Leys, C., Ley, C., Klein, O., Bernard, P., & Licata, L. (2013). 
            Detecting outliers: Do not use standard deviation around the mean, use absolute deviation around the 
            median. Journal of Experimental Social Psychology, 49(4), 764–766. 
            https://doi.org/10.1016/j.jesp.2013.03.013*
            
            2. **IQR** Tukey's Inter Quartile Range
            
            *Tukey, JW. (1977) Exploratory data analysis. Addison Wesely*
            
            3. **SD** Standard Deviation (Z Score)
             
             *Aggarwal, C.C. (2017). An Introduction to Outlier Analysis. In: Outlier Analysis. Springer, Cham. 
             https://doi.org/10.1007/978-3-319-47578-3_1*
            """
        )
    return user_formula


def distribution_graph(distribution: pd.DataFrame, formula: Formula, kind='KDE'):
    """
    Display a KDE plot or a histogram on a streamlit app showing threshold calculated from an outlier detection formula.
    :param distribution: Dataframe with column 'Distribution' with values and column 'Type' with data type.
    :param formula: Outlier detection formula
    :param kind: Kind of dataframe to show (KDE or histogram)
    :return: None
    """
    # Set the background color and create a kernel density estimate plot without bars
    sns.set_theme()
    fig = plt.figure()

    # Create a KDE plot with different colors based on the "Type" column
    try:
        if kind.startswith('KDE'):
            ax = sns.kdeplot(data=distribution, x='Distribution', hue='Type', fill=True, common_norm=True, legend=True)
        else:
            ax = sns.histplot(data=distribution, x='Distribution', hue='Type', fill=True, common_norm=True, legend=True)

        # Set labels
        plt.xlabel('Value')
        plt.ylabel('Density')

        distribution_ndarray = distribution['Distribution'].__array__()

        # Calculate threshold and indicate it on the graph with vertical lines
        threshold = get_threshold(data=distribution_ndarray, weight_mad=formula.mad_weight,
                                  weight_iqr=formula.iqr_weight, weight_sd=formula.sd_weight,
                                  weight_adjusted_mad=formula.adjusted_mad_weight,
                                  const_mad=formula.mad_constant,
                                  const_iqr=formula.iqr_constant, const_sd=formula.sd_constant,
                                  const_adjusted_mad=formula.adjusted_mad_constant)
        ax.axvline(x=threshold[0], color='blue', linestyle='--')
        ax.axvline(x=threshold[1], color='blue', linestyle='--')

        # Legend
        sns.move_legend(ax, loc='upper right')
        plt.setp(ax.get_legend().get_texts(), fontsize='8')  # for legend text
        plt.setp(ax.get_legend().get_title(), fontsize='10')  # for legend title

        # Show graph
        with st.container(border=True):
            st.pyplot(fig)
    except TypeError:
        st.error('The chosen column is not numeric. Please choose another column.')


def get_plot_kind():
    """
    Allow user to select kind of plot from sidebar on a streamlit app.
    :return: Plot kind.
    """
    plot_kind = st.sidebar.radio(label='Plot kind', options=['KDE Plot', 'Histogram'])
    return plot_kind
