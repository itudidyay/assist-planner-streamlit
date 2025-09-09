import streamlit as st
import pandas as pd
import requests, json
import app_functions

st.set_page_config(page_title="See articulations from a CCC to multiple four-years",
                   page_icon="📈",
                   layout="wide")

st.write("Work in Progress...")

# year = st.number_input("Enter start year", min_value=2023, value=2024, step=1)
# year_id = year - 1949

# with st.form("cc_selection"):
#     cc_selections = st.multiselect("CCC",
#                                 app_functions.get_CC_data(),
#                                 format_func=app_functions.display_names_codes)
#     st.form_submit_button("See four year unversities")
    

# with st.form("fy_selection"):
#     four_year_selection = st.selectbox(
#     "Select four year universities",
#     app_functions.get_four_year_data(),
#     format_func=app_functions.display_names_codes,
#     disabled=not bool(cc_selections))
#     st.form_submit_button("See majors")

# with st.form("major_selection"):
#     major_selections = st.multiselect("Majors",
#                                 app_functions.get_majors_data(cc_selections[0]['id'],four_year_selection['id'],year_id),
#                                 format_func=app_functions.display_label_major,
#                                 disabled=not bool(four_year_selection))
#     major_submit = st.form_submit_button("Submit")

# st.write(cc_selections, four_year_selection, major_selections, st.session_state)