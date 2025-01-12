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
        # Download the data
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)

        # Debug: Show available columns
        st.write(f"Available columns for {ticker}: {list(data.columns)}")

        if data.empty:
            return None, f"No data available for {ticker}."

        # Handle multi-level columns
        if isinstance(data.columns, pd.MultiIndex):
            # Extract the column corresponding to the ticker
            if ("Adj Close", ticker) in data.columns:
                price_column = ("Adj Close", ticker)
            elif ("Close", ticker) in data.columns:
                price_column = ("Close", ticker)
            else:
                return None, f"No suitable price column ('Adj Close' or 'Close') found for {ticker}."
            prices = data[price_column]
        else:
            # Single-level column handling
            if "Adj Close" in data.columns:
                prices = data["Adj Close"]
            elif "Close" in data.columns:
                prices = data["Close"]
            else:
                return None, f"No suitable price column ('Adj Close' or 'Close') found for {ticker}."

        # Calculate returns
        returns = prices.pct_change().dropna()
        return returns, None
    except Exception as e:
        return None, f"Error fetching data for {ticker}: {e}"

def generate_quantstats_report(returns, benchmark_returns, report_type):
    """Generate QuantStats report and return HTML content."""
    try:
        if report_type == "Basic":
            # Generate basic metrics report
            return qs.reports.metrics(returns, benchmark=benchmark_returns, mode="basic")
        elif report_type == "Full":
            # Generate full QuantStats report
            return qs.reports.full(returns, benchmark=benchmark_returns, output=None)
        elif report_type == "Detailed":
            # Generate detailed QuantStats HTML report
            return qs.reports.html(returns, benchmark=benchmark_returns, output=None)
        else:
            raise ValueError(f"Invalid report type: {report_type}")
    except Exception as e:
        raise Exception(f"Error generating QuantStats report: {e}")

if st.button("Generate Report"):
    with st.spinner(f"Fetching data for {ticker} and {benchmark}..."):
        # Fetch stock and benchmark returns
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
                try:
                    # Generate the report
                    report_html = generate_quantstats_report(stock_returns, benchmark_returns, report_type)

                    # Display the report in the Streamlit app
                    if report_html:
                        st.components.v1.html(report_html, height=800, scrolling=True)
                    else:
                        st.error("Failed to generate report content.")
                except Exception as e:
                    st.error(f"Error generating QuantStats report: {e}")



st.markdown("---")
st.markdown("""
### About This App
This app uses QuantStats and Yahoo Finance to analyze stock/ETF performance. Enter a ticker, select a date range, and generate a detailed performance report.
""")
