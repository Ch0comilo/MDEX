import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Modelo BIBD")

df = st.session_state.get("df") # <-- Con este pueden trabajar, no hay que subir otro archivo