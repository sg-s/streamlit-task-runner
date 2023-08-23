import streamlit as st
from streamlit_task_runner import run_task, show_results

st.write("# Task runner")
st.write(
    """This page demonstrates how we can run a long
    running task in streamlit, capture output and live
    and display it to the user.

This is designed to work with any shell command,
and here we use ping to simulate a long-running task.

    """
)

n_ping = st.number_input(
    "Number of ping packets",
    min_value=3,
    max_value=20,
    step=1,
)

cmd = f"ping -c {n_ping} google.com"
cmd = cmd.split()


empty_container = st.empty()


do_stuff = st.button(
    "Run",
    on_click=run_task,
    kwargs={"command": cmd, "container": empty_container},
)

show_results(command=cmd)
