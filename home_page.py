import streamlit as st 
import matplotlib.pyplot as plt
import numpy as np

## for the warnings
st.set_option('deprecation.showPyplotGlobalUse', False)

## general page configuration 
st.set_page_config(
    page_title="Bingo",
    page_icon=":smiley:",
    layout="wide",
    initial_sidebar_state="collapsed")

## title 
st.title("Locaria Bingo!")

## sidebar
# st.sidebar.markdown("# Locaria Bingo!")

## main page 
st.markdown("## Welcome to Locaria Bingo!")
st.markdown("### How to Use?")
st.markdown("1. Fill in the desired parameters of the bingo card.")
st.markdown("2. Click on the button to generate the bingo card.")
st.markdown("3. If you're satisfied, save the bingo card(s).")



## parameters
st.markdown("## Parameters")
st.markdown("### Number of Bingo Cards")
num_cards = st.number_input("Number of Bingo Cards", min_value=1, max_value=200, value=1, step=1)


## number of rows and columns
st.markdown("### Number of Rows and Columns")
## make columns so it fits on the page
col1, col2 = st.columns(2)
num_rows = col1.number_input("Number of Rows", min_value=1, max_value=10, value=5, step=1)
num_cols = col2.number_input("Number of Columns", min_value=1, max_value=10, value=5, step=1)

## minimum and maximum values
st.markdown("### Minimum and Maximum Values")
col3, col4 = st.columns(2)
min_val = col3.number_input("Minimum Value", min_value=1, max_value=101, value=1, step=1)
max_val = col4.number_input("Maximum Value", min_value=1, max_value=101, value=101, step=1)


## advanced options 
with st.expander("Advanced Options"):
    ### create three columns 
    cola, colb, colc = st.columns(3)
    cola.markdown("#### Multiplier for Spacing")
    cola.write("Modifies the size of the grid, either increasing it or decreasing it.")
    cola.write("The default value is 2.0.")
    spacing_multiplier = cola.number_input("Multiplier", min_value=1.0, max_value=10.0, value=2.0, step=0.1)
    ## free space value 
    colb.markdown("#### Free Space Value")
    colb.write("This is the value that will be placed in the free space on the bingo card.")
    colb.write("The default value is 'FREE'.")
    free_space_value = colb.text_input("Free Space Value", value="FREE")
    ## free space location
    colc.markdown("#### Free Space Location")
    colc.write("This is the location of the free space on the bingo card.")
    colc.write("The default value is 'center'. (number of rows modulo 2)")
    free_space_coordinates = colc.number_input("Free Space Location", min_value=1, max_value=100, value=num_rows // 2, step=1)