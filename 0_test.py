import streamlit as st
import pandas as pd
from utils import *
from typing import List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.write('Hello, world!')

st.write(1+1)

#@st.cache_data
df = pd.read_excel("/Users/x/Documents/GitHub/analysis/Pro/2022/FIBA_3x3_Pro_Circuit_Stats_After_028_Events.xlsx")
st.dataframe(df, use_container_width=True)

#st.write(df.head())