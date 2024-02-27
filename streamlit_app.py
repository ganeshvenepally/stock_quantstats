import streamlit as st
import quantstats as qs
import yfinance as yf

# Set page config
st.set_page_config(page_title="ETF Quantstats Report", layout="wide")

# Sidebar - Collects user input for different ETFs
etf_input = st.sidebar.text_input("Enter ETF symbol", value="SPY").upper()

# Download historical data for ETF
@st.cache
def load_data(ticker):
    data = yf.download(ticker, start="2010-01-01")
    return data

try:
    etf_data = load_data(etf_input)
    if not etf_data.empty:
        # Display some basic information about the ETF
        st.write(f"ETF Symbol: {etf_input}")
        st.write("ETF Historical Data:")
        st.line_chart(etf_data['Close'])

        # Generate and display Quantstats report
        st.header("Quantstats Report")
        qs.reports.html(etf_data['Close'], output='streamlit')  # This will display the report within the Streamlit app
    else:
        st.error("Error: No data found for the specified ETF symbol. Please try another one.")
except Exception as e:
    st.error(f"An error occurred: {e}")
