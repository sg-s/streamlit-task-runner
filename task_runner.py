import streamlit as st
from streamlit_task_runner import run_task, show_results

st.write("# Task runner")


cmd = "ping -c 3 google.com"
cmd = cmd.split()


empty_container = st.empty()


do_stuff = st.button(
    "Do stuff",
    on_click=run_task,
    kwargs={"command": cmd, "container": empty_container},
)

show_results(command=cmd)
