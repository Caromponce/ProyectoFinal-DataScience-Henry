import streamlit as st


def henry_title(text):

    st.markdown(
        f"""
        <h1>
        <span class="henry-highlight">{text}</span>
        </h1>
        """,
        unsafe_allow_html=True
    )


def henry_tag(text):

    st.markdown(
        f"""
        <span class="henry-tag">&lt;{text}&gt;</span>
        """,
        unsafe_allow_html=True
    )


def henry_card(title, content):

    st.markdown(
        f"""
        <div class="henry-card">

        <h4>{title}</h4>

        <p>{content}</p>

        </div>
        """,
        unsafe_allow_html=True
    )


def henry_bullet(text):

    st.markdown(
        f"""
        <span class="henry-bullet">➜</span> {text}
        """,
        unsafe_allow_html=True
    )


def henry_metric(label, value):

    st.metric(label, value)