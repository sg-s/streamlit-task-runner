import asyncio
import hashlib
import os
import subprocess

import streamlit as st
from beartype import beartype
from beartype.typing import List


def _start():
    """set up task_runner dict in session state
    if needed

    Do not call this directly.
    """
    if "task_runner" not in st.session_state:
        st.session_state.task_runner = dict()


async def _update_task_log(
    *,
    process: subprocess.Popen,
    container: st.delta_generator.DeltaGenerator,
    nonce: str = "",
):
    """Core event loop. Checks process for completion
    and checks stdout file. Updates container with contents
    of stdout

    Do not call this directly.

    """

    stdout_file = f"/tmp/STDOUT-{nonce}.txt"
    stderr_file = f"/tmp/STDERR-{nonce}.txt"

    go_on = True
    while go_on:
        # check if process is still running
        if process.poll() is not None:
            go_on = False

        with container:
            if os.path.exists(stdout_file):
                with open(stdout_file, "r") as file:
                    data = file.read()
                st.code(data)

        await asyncio.sleep(0.1)


@beartype
def show_results(command: List[str]):
    _start()
    hash = _hash_command(command)

    if hash not in st.session_state.task_runner.keys():
        return

    exit_code = st.session_state.task_runner[hash]["exit_code"]
    if exit_code != 0:
        heading = f"❌ Task failed with code {exit_code}"
    else:
        heading = "✅ Task completed successfully"

    with st.expander(heading, expanded=exit_code != 0):
        st.write("### Command")
        st.code("\n".join(command), language="bash")

        stdout = st.session_state.task_runner[hash]["stdout"]
        if stdout:
            st.write("### Output:")
            st.code(stdout, language="bash")

        stderr = st.session_state.task_runner[hash]["stderr"]
        if stderr:
            st.write("### Error:")
            st.error(stderr)


def _hash_command(command: List[str]) -> str:
    """util function to convert a list of strings into a hash"""
    return hashlib.sha1(" ".join(command).encode("utf-8")).hexdigest()


def run_task(
    *,
    command: List[str],
    container,
    nonce: str = "",
):
    _start()
    hash = _hash_command(command)

    st.session_state.task_runner[hash] = dict(
        stdout=None,
        stderr=None,
    )

    stdout_file = f"/tmp/STDOUT-{nonce}.txt"
    stderr_file = f"/tmp/STDERR-{nonce}.txt"

    with open(stdout_file, "w") as stdout, open(stderr_file, "w") as stderr:
        process = subprocess.Popen(
            command,
            stdout=stdout,
            stderr=stderr,
        )

    with asyncio.Runner() as runner:
        runner.run(
            _update_task_log(
                container=container,
                process=process,
            )
        )

        runner.close()

    st.session_state.task_runner[hash]["exit_code"] = process.poll()

    # read in stdout
    with open(stdout_file, "r") as file:
        st.session_state.task_runner[hash]["stdout"] = file.read()

    # read in stderr
    with open(stderr_file, "r") as file:
        st.session_state.task_runner[hash]["stderr"] = file.read()
