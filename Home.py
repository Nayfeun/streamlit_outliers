import streamlit as st


def main():
    ### Config ###
    st.set_page_config(
        page_title="Outlier Detection",
        layout="centered",
    )

    st.sidebar.success('Please select a page above')

    st.title("Outlier Threshold Visualizer")
    st.markdown(
        """
        ## Context
        Outliers can significantly affect statistical analyses, machine learning models, and decision-making processes. 
        However, choosing the right outlier detection method can be challenging. Researchers often default to a specific
        method without fully understanding its implications. This app addresses this issue by allowing users to explore
        various univariate outlier detection techniques and visualize the resulting thresholds.

        ### How It Works 
        1. **Select a Method**: Choose from a list of commonly used outlier detection methods, such as Z-score, Tukey's 
        method, or Median Absolute Deviation. 
        2. **Upload Your Data**: Load your dataset or build a distribution directly. 
        3. **Visualize the Threshold**: The app will calculate the threshold for the chosen method and display it on a
         figure.

        ### Simulation 
        In the "Simulation" section, you can create custom distributions by adjusting parameters like distribution
        shape, size, and adding outliers from a selection of different shapes. You can then explore how different
        outlier detection methods would impact the distribution you built.

        ### Visualization
        The "Visualization" section allows you to upload your own dataset. You can then see how each outlier detection
        method influences your data distribution.
        """
    )

if __name__ == '__main__':
    main()
