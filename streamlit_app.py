import streamlit as st
import yfinance as yf
import quantstats as qs
import pandas as pd
from datetime import datetime, timedelta
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Extend pandas with QuantStats functionality
qs.extend_pandas()

# Configure the Streamlit app
st.set_page_config(
    page_title="Stock/ETF Analysis with QuantStats",
    page_icon="📈",
    layout="wide"
)

st.title("📊 Stock/ETF Performance Analysis")
st.markdown("Generate detailed performance analysis reports for any stock or ETF listed on Yahoo Finance.")

# Input fields
col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input("Enter Stock/ETF Symbol:", value="SPY").upper()

with col2:
    start_date = st.date_input("Start Date:", value=datetime.now() - timedelta(days=365 * 3))

with col3:
    end_date = st.date_input("End Date:", value=datetime.now())

benchmark = st.selectbox(
    "Select Benchmark:",
    options=["SPY", "^GSPC", "^DJI", "^IXIC"],
    format_func=lambda x: {
        "SPY": "S&P 500 ETF (SPY)",
        "^GSPC": "S&P 500 Index (^GSPC)",
        "^DJI": "Dow Jones Industrial Average (^DJI)",
        "^IXIC": "NASDAQ Composite (^IXIC)"
    }[x]
)

report_type = st.radio(
    "Select Report Type:", ["Basic", "Full", "Detailed"], horizontal=True
)

def download_stock_data(ticker, start_date, end_date):
    """Download stock data from Yahoo Finance and calculate returns."""
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            return None, f"No data available for {ticker}."

        # Check for the column to use
        price_column = None
        if "Adj Close" in data.columns:
            price_column = "Adj Close"
        elif "Close" in data.columns:
            price_column = "Close"
        else:
            return None, f"No suitable price column ('Adj Close' or 'Close') found for {ticker}."

        # Calculate returns
        returns = data[price_column].pct_change().dropna()
        return returns, None
    except Exception as e:
        return None, f"Error fetching data for {ticker}: {e}"


def generate_quantstats_report(returns, benchmark_returns, report_type):
    """Generate QuantStats report."""
    try:
        from io import StringIO
        output = StringIO()
        if report_type == "Basic":
            qs.reports.metrics(returns, mode="basic", benchmark=benchmark_returns, output=output)
        elif report_type == "Full":
            qs.reports.full(returns, benchmark=benchmark_returns, output=output)
        else:
            qs.reports.html(returns, benchmark=benchmark_returns, output=output)
        return output.getvalue()
    except Exception as e:
        return f"Error generating QuantStats report: {e}"

if st.button("Generate Report"):
    with st.spinner(f"Fetching data for {ticker} and {benchmark}..."):
        stock_returns, stock_error = download_stock_data(ticker, start_date, end_date)
        benchmark_returns, bench_error = download_stock_data(benchmark, start_date, end_date)

        if stock_error:
            st.error(stock_error)
        elif bench_error:
            st.error(bench_error)
        else:
            st.info(f"Fetched {len(stock_returns)} data points for {ticker}.")
            st.info(f"Fetched {len(benchmark_returns)} data points for {benchmark}.")

            with st.spinner("Generating QuantStats report..."):
                report_content = generate_quantstats_report(stock_returns, benchmark_returns, report_type)
                if report_content:
                    st.components.v1.html(report_content, height=800, scrolling=True)
                else:
                    st.error("Failed to generate report.")

st.markdown("---")
st.markdown("""
### About This App
This app uses QuantStats and Yahoo Finance to analyze stock/ETF performance. Enter a ticker, select a date range, and generate a detailed performance report.
""")
