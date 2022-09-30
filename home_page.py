import shutil
import streamlit as st 
import matplotlib.pyplot as plt
import numpy as np
import zipfile
import os
import base64
import tempfile 
import pandas as pd 

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

## upload a file here with text 
uploaded_file = st.file_uploader("Choose a file with text", type="xlsx")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, header=None)
    ## drop duplicates 
    df = df.drop_duplicates()
    ## now get the text from the file
    prompts = df[0].tolist()

## show the number of prompts in the file
if uploaded_file is not None:
    st.info(f"There are {len(prompts)} prompts in the file.")
    default_num_cards = len(prompts)


with st.expander("Parameters"):
    ## parameters
    st.markdown("### Number of Bingo Cards")
    if uploaded_file is not None:
        num_cards = st.number_input("Number of Bingo Cards", min_value = 1, max_value = 200, value = default_num_cards, step = 1)
    else:
        num_cards = st.number_input("Number of Bingo Cards", min_value=1, max_value=200, value=10, step=1)
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
    
    ## colors 
    st.markdown("### Colors")
    ## show a set of colors which are pre-defined options
    colors = ["#871882", "#17DDBF", "#FF8850", "#CCE161"]



## advanced options 
with st.expander("Advanced Options"):
    ### create three columns 
    cola, colb, colc,cold = st.columns(4)
    cola.write("Multiplier for Spacing")
    cola.write("Modifies the size of the grid, either increasing it or decreasing it.")
    cola.write("The default value is 2.0.")
    spacing_multiplier = cola.number_input("Multiplier", min_value=1.0, max_value=10.0, value=2.0, step=0.1)
    ## free space value 
    colb.markdown("Free Space Value")
    colb.write("This is the value that will be placed in the free space on the bingo card.")
    colb.write("The default value is 'FREE'.")
    free_space_value = colb.text_input("Free Space Value", value="FREE")
    ## free space location
    colc.markdown("Font Size")
    colc.write("This is the font size of the text on the bingo card.")
    colc.write("The default value is 10.")
    font_size = colc.number_input("Font Size", min_value=1, max_value=100, value=10, step=1)
    free_space_coordinates = (num_cols//2, num_rows//2)
    ## maximum size for text 
    cold.markdown("Maximum Size for Text")
    cold.write("This is the maximum size for the text on the bingo card.")
    cold.write("The default value is 3 (words).")
    MAX_SIZE = cold.number_input("Maximum Size", min_value=1, max_value=10, value=3, step=1)

## CONSTANTS
FIGURE_SIZE = (num_cols * spacing_multiplier, num_rows * spacing_multiplier)
TOTAL_NUMBERS = num_cols * num_rows - 1

def create_bingo_card():
    ## CREATING THE FIGURE 
    fig = plt.figure(figsize=FIGURE_SIZE)
    ax = fig.add_subplot(111)

    ## MAKING THE GRID
    for x in range(num_cols):
        for y in range(num_rows):
            ax.plot([x, x+1], [y, y], color='black')
            ax.plot([x, x], [y, y+1], color='black')
            ax.plot([x+1, x+1], [y, y+1], color='black')
            ax.plot([x, x+1], [y+1, y+1], color='black')
    ax.axis('off')
    return ax

def get_random_color():
    return np.random.choice(colors)

def color_free_slot(some_ax,color):
    some_ax.add_patch(plt.Rectangle((free_space_coordinates[0], free_space_coordinates[1]), 1, 1, color=color))

def text_free_slot(some_ax, text):
    some_ax.text(free_space_coordinates[0]+0.5, free_space_coordinates[1]+0.5, text, horizontalalignment='center', verticalalignment='center', fontsize=20)

def get_random_numbers():
    my_numbers = np.random.choice(np.arange(min_val,max_val), size=TOTAL_NUMBERS, replace=False)
    np.random.shuffle(my_numbers)
    return my_numbers

def fill_grid(some_ax,numbers_list):
    ## FILLING THE GRID
    numbers = numbers_list
    for x in range(num_cols):
        for y in range(num_rows):
            if (x, y) != free_space_coordinates:
                ## choose a random number from the list numbers and remove it from the list
                number = numbers[0]
                ## make sure that the same color is not used twice in adjacent cells
                some_ax.text(x+0.5, y+0.5, number, horizontalalignment='center', verticalalignment='center', fontsize=20)
                numbers = numbers[1:]

def fill_grid_textual(some_ax,text_list):
    ## FILLING THE GRID
    texts = text_list
    for x in range(num_cols):
        for y in range(num_rows):
            if (x, y) != free_space_coordinates:
                ## choose a random number from the list texts and remove it from the list
                the_text = texts[0]
                ## make sure that the same color is not used twice in adjacent cells
                ## if the text is longer than 4 words, but less than 6 words, split it into two lines and make the font smaller
                if len(str(the_text).split()) > MAX_SIZE and len(str(the_text).split()) <= MAX_SIZE*2:
                    ## join the text with a newline between the words 
                    txt = " ".join(str(the_text).split()[:MAX_SIZE]) + "\n" + " ".join(str(the_text).split()[MAX_SIZE:])
                ## if it is greater than 6 words, split it into three lines and make the font even smaller
                elif len(str(the_text).split()) > MAX_SIZE*2:
                    txt = " ".join(str(the_text).split()[:MAX_SIZE]) + "\n" + " ".join(str(the_text).split()[MAX_SIZE:MAX_SIZE*2]) + "\n" + " ".join(str(the_text).split()[MAX_SIZE*2:])
                else:
                    txt = str(the_text)
                some_ax.text(x+0.5, y+0.5, txt, horizontalalignment='center', verticalalignment='center', fontsize=font_size)
                texts = texts[1:]
    return some_ax

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

def run_generator(numeric_textual:str):
    bingo_card = create_bingo_card()
    ## color the free slot
    free_slot_color = get_random_color()
    color_free_slot(bingo_card, free_slot_color)
    ## add text to the free slot
    text_free_slot(bingo_card, free_space_value)
    ## fill the grid with random numbers
    numbers = get_random_numbers()
    if numeric_textual == "numeric":
        fill_grid(bingo_card,numbers)
    elif numeric_textual == "textual":
        ## shuffle the list of words
        np.random.shuffle(prompts)
        fill_grid_textual(bingo_card,prompts)
    this_figure = bingo_card.figure
    return this_figure

## create 3 columns 
generate_numeric_cards,generate_textual_cards,save_cards = st.columns(3)



## button to generate the bingo card
if generate_numeric_cards.button("Preview: Numeric Bingo Card"):
    ## generate the bingo card
    this_figure = run_generator(numeric_textual="numeric")
    ## display the figure in a smaller size
    st.pyplot(this_figure, dpi=100)

## button to generate the bingo card
if generate_textual_cards.button("Preview: Textual Bingo Card"):
    ## generate the bingo card
    this_figure = run_generator(numeric_textual="textual")
    ## display the figure in a smaller size
    st.pyplot(this_figure, dpi=100)


## create the save cards button 
if save_cards.button("Save Bingo Card"):
    with st.spinner("Saving the bingo cards..."):
        ## create a directory called bingo_cards, if it exists, delete it 
        if os.path.exists("bingo_cards"):
            shutil.rmtree("bingo_cards")
        os.mkdir("bingo_cards")
        ## start generating the bingo cards, each with a new folder 
        for i in range(1, num_cards+1):
            ## make the directory 
            os.mkdir(f"bingo_cards/bingo_card_{i}")
            ## create the numeric bingo card
            numeric_bingo_card = run_generator(numeric_textual="numeric")
            ## save the numeric bingo card
            numeric_bingo_card.savefig(f"bingo_cards/bingo_card_{i}/bingo_numeric_card_{i}.png")
            ## clear the figure
            plt.clf()
            plt.close()
            ## create the textual bingo card
            textual_bingo_card = run_generator(numeric_textual="textual")
            ## save the figure to the directory
            textual_bingo_card.savefig(f"bingo_cards/bingo_card_{i}/bingo_textual_card_{i}.png")
        ## create a zip file of the bingo cards
        shutil.make_archive("bingo_cards", "zip", "bingo_cards")
        ## delete the directory of bingo cards
        shutil.rmtree("bingo_cards")
        ## 3 columns 
        _, download_bingo_cards, _ = st.columns(3)
        ## download the zip file
        download_bingo_cards.markdown(get_binary_file_downloader_html("bingo_cards.zip", 'Bingo Cards'), unsafe_allow_html=True)
        ## delete the zip file
        os.remove("bingo_cards.zip")
    ## success 
    st.success("Bingo cards saved!")
    ## balloon notification
    st.balloons()

## add a divider
st.markdown("""---""")
## add the section: Draw random numbers 
st.header("Draw random number")
# initializing with a random number
if "rn" not in st.session_state:
    st.session_state["rn"] = set()

rng_button, rng_text = st.columns(2)

## add a button to draw random numbers
if rng_button.button("Draw random numbers"):
    ## get the random numbers
    random_numbers = np.random.randint(1,101,size=1)[0]
    if random_numbers in st.session_state.rn: 
        st.warning("This number has already been drawn!")
    else: 
        st.success(f"Number drawn: {random_numbers}")
        st.success(f"Number of numbers drawn: {len(st.session_state.rn)+1}")
        st.session_state.rn.add(random_numbers)
        ## show the numbers that have been drawn
        st.write(f"Numbers drawn: {sorted(list(st.session_state.rn))}")
        st.balloons()
## same for the texts 
## add a divider
st.markdown("""---""")
## add the section: Draw random numbers 
st.header("Draw random prompt")
# initializing with a random number
if "rp" not in st.session_state:
    st.session_state["rp"] = set()

rng_button, rng_text = st.columns(2)

## add a button to draw random numbers
if rng_button.button("Draw random prompt"):
    ## get the random numbers
    random_text = np.random.choice(prompts,1)[0]
    if random_text in st.session_state.rp: 
        st.warning("This text has already been drawn!")
    else: 
        st.success(f"Prompt drawn: {random_text}")
        st.success(f"Number of Prompts drawn: {len(st.session_state.rp)+1}")
        st.session_state.rp.add(random_text)
        ## show the numbers that have been drawn
        st.write(f"Prompt drawn: {sorted(list(st.session_state.rp))}")
        st.balloons()

