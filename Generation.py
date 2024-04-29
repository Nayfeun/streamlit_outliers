import streamlit as st
from scipy.stats import skewnorm
import matplotlib.pyplot as plt
import seaborn as sns

PARAMETERS = ['mean', 'standard deviation', 'size', 'skewness']


def get_parameters():
    mean = st.number_input('Mean')
    sd = st.number_input('Standard deviation', value=1.)
    n = st.number_input('Size', min_value=0, step=1, value=10000)
    skewness = st.slider('Skewness', min_value=-10., max_value=+10., value=0., step=0.01)
    return mean, sd, n, skewness


def create_graph(data):
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.kdeplot(data)
    return fig


def main():
    fig_container = st.container()
    mean, sd, n, skewness = get_parameters()
    generated_distribution = skewnorm.rvs(skewness, loc=mean, scale=sd, size=n)
    fig_container.pyplot(create_graph(generated_distribution))


if __name__ == '__main__':
    main()
