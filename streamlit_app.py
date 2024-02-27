import streamlit as st
import quantstats as qs
import yfinance as yf
from datetime import datetime

# Set page config
st.set_page_config(page_title="ETF Quantstats Report", layout="wide")

# Sidebar - Collects user input
etf_input = st.sidebar.text_input("Enter ETF symbol", value="SPY").upper()
benchmark_input = st.sidebar.text_input("Enter Benchmark symbol", value="QQQ").upper()
start_date = st.sidebar.date_input("Start Date", datetime(2010, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.now())

# Download historical data
@st.cache
def load_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

try:
    # Load ETF and Benchmark data
    etf_data = load_data(etf_input, start_date, end_date)
    benchmark_data = load_data(benchmark_input, start_date, end_date)

    if not etf_data.empty and not benchmark_data.empty:
        # Display some basic information about the ETF and Benchmark
        st.write(f"ETF Symbol: {etf_input} | Benchmark Symbol: {benchmark_input}")
        st.write("ETF Historical Data:")
        st.line_chart(etf_data['Close'])

        st.write("Benchmark Historical Data:")
        st.line_chart(benchmark_data['Close'])

        # Generate and display Quantstats report
        st.header("Quantstats Report")

        # Creating combined returns for better comparison
        combined_returns = qs.utils.make_index(etf_data['Close']).pct_change().fillna(0)
        benchmark_returns = qs.utils.make_index(benchmark_data['Close']).pct_change().fillna(0)
        
        # Benchmarked Report
        qs.reports.html(combined_returns, benchmark=benchmark_returns, output='streamlit')
    else:
        st.error("Error: No data found for the specified symbols. Please try another one.")
except Exception as e:
    st.error(f"An error occurred: {e}")
