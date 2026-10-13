import streamlit as st
import time

st.set_page_config(page_title = "CausalLens Dashboard", page_icon = "🚀")

#Title and some text
st.title("Turbofan Engine Diagnostic Dashboard")
st.write("This is the frontend UI for our senior project.")

#Create an interactive button
#Everything indented under the button only happens when clicked
if st.button("Click me!"):
    with st.spinner("Wait for it..."):
        time.sleep(5)
        
    st.success("It worked! You clicked the button.")
    st.balloons()