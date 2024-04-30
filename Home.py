import streamlit as st


def main():
    ### Config ###
    st.set_page_config(
        page_title="Outlier Detection",
        layout="centered",
    )

    st.sidebar.success('Please select a page above')

    st.write('# Hello')
    st.write('## *Explanations*')


if __name__ == '__main__':
    main()
