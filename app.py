import streamlit as st
import pandas as pd

# Display the main page title and a one-line description
st.title("MacroMarket")
st.write("Explore how U.S. economic conditions move alongside the stock market.")

# Load the saved FRED unemployment data from the data folder
df = pd.read_csv("data/UNRATE.csv")

# Convert the date column from plain text into real datetime objects
df["observation_date"] = pd.to_datetime(df["observation_date"])

# Set the date column as the DataFrame index so Streamlit uses it for the x-axis
df = df.set_index("observation_date")

# Plot the unemployment rate over time as an interactive line chart
st.subheader("U.S. Unemployment Rate (%)")
st.line_chart(df["UNRATE"])

# Display the underlying data as a scrollable table below the chart
st.subheader("Historical Data")
st.dataframe(df)