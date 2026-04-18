#############################################################################
# internals.py
#
# This file contains internals for component templating. You do not need
# to understand this file, but are welcome to read through it if you want.
#
#############################################################################

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

REPO_ROOT = Path(__file__).resolve().parent
CUSTOM_COMPONENTS_DIR = REPO_ROOT / "custom_components"


def load_html_file(file_path):
    """Read an HTML (or CSS) file relative to repo root or custom_components."""
    path = Path(file_path)
    if not path.is_absolute():
        if str(file_path).startswith("custom_components/"):
            path = REPO_ROOT / file_path
        else:
            path = CUSTOM_COMPONENTS_DIR / file_path
    with open(path, encoding="utf-8") as file:
        return file.read()


def load_iframe_base_css():
    return load_html_file("iframe_base.css")


def inject_streamlit_global_styles():
    """Inject shared Streamlit (main document) styles from custom_components."""
    css = load_html_file("streamlit_global.css")
    st.markdown(f"<style>\n{css}\n</style>", unsafe_allow_html=True)


def _inject_iframe_base_into_html(html: str) -> str:
    """Prepend iframe_base.css in a <style> block after <head> if present, else at top."""
    base_css = load_iframe_base_css()
    style_block = f"<style>\n{base_css}\n</style>"
    lower = html.lower()
    head_pos = lower.find("<head>")
    if head_pos != -1:
        insert_at = head_pos + len("<head>")
        return html[:insert_at] + "\n" + style_block + html[insert_at:]
    return style_block + "\n" + html


def safe_string(string):
    # Make the string "safe" by escaping quotes and a backslash character
    return ''.join(['\\' + c if c in ["'", '"', '\\'] else c for c in string])


def create_component(data, component_name, height=None, width=None, scrolling=True):
    component_path = CUSTOM_COMPONENTS_DIR / f"{component_name}.html"
    with open(component_path, encoding="utf-8") as file:
        component_html = file.read()

    component_html = _inject_iframe_base_into_html(component_html)

    for key in data:
        data_placeholder = "{{" + str(key) + "}}"
        component_html = component_html.replace(
            data_placeholder, safe_string(str(data[key])))

    components.html(component_html, width, height, scrolling)
