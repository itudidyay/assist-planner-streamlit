import streamlit as st

st.cache_data.clear()

pages = [
    st.Page("CCC_To_Multiple_Four_Years.py", title="CCC to Four Year"),
    st.Page("Multiple_CCCs_To_Four_Year.py", title="Multiple CCCs to Four Year")
    ]
pg = st.navigation(pages)
pg.run()
