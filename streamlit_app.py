import streamlit as st
import yfinance as yf
import quantstats as qs
import pandas as pd
from datetime import datetime, timedelta
import tempfile
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure QuantStats to use HTML display
qs.extend_pandas()

# Configure the page
st.set_page_config(
    page_title="Stock/ETF Analysis with QuantStats",
    page_icon="📈",
    layout="wide"
)

# Main title
st.title("📊 Stock/ETF Performance Analysis")
st.markdown("Generate detailed performance analysis reports for any stock or ETF listed on Yahoo Finance.")

# Input section
col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input("Enter Stock/ETF Symbol:", value="SPY").upper()
    
with col2:
    start_date = st.date_input(
        "Start Date:",
        value=datetime.now() - timedelta(days=365*3)
    )
    
with col3:
    end_date = st.date_input(
        "End Date:",
        value=datetime.now()
    )

# Benchmark selection
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

# Report type selection
report_type = st.radio(
    "Select Report Type:",
    ["Basic", "Full", "Detailed"],
    horizontal=True
)

def get_stock_data(ticker, start_date, end_date):
    """Fetch stock data with error handling and column checking"""
    try:
        # Create ticker object
        ticker_obj = yf.Ticker(ticker)
        
        # Get historical data
        df = ticker_obj.history(start=start_date, end=end_date)
        
        # Check if df is empty
        if df.empty:
            return None, f"No data found for {ticker}"
            
        # Convert index timezone to UTC and then remove timezone info
        df.index = df.index.tz_convert('UTC').tz_localize(None)
        
        # Try different possible column names
        if 'Adj Close' in df.columns:
            return df['Adj Close'], None
        elif 'Close' in df.columns:
            return df['Close'], None
        else:
            return None, f"Could not find price data for {ticker}"
            
    except Exception as e:
        return None, str(e)

def align_data(stock_data, benchmark_data):
    """Align stock and benchmark data to have the same dates"""
    # Get common dates
    common_dates = stock_data.index.intersection(benchmark_data.index)
    
    # Reindex both series to common dates
    stock_data = stock_data[common_dates]
    benchmark_data = benchmark_data[common_dates]
    
    return stock_data, benchmark_data

def generate_quantstats_report(stock_data, benchmark_data, report_type):
    """Generate QuantStats report and return HTML content directly"""
    try:
        # Create a StringIO object to capture the HTML output
        from io import StringIO
        output = StringIO()
        
        # Generate the report based on type
        if report_type == "Basic":
            qs.reports.basic(stock_data, benchmark_data, output=output)
        elif report_type == "Full":
            qs.reports.full(stock_data, benchmark_data, output=output)
        else:  # Detailed
            qs.reports.html(stock_data, benchmark_data, output=output)
        
        # Get the HTML content
        html_content = output.getvalue()
        output.close()
        
        return html_content, None
    except Exception as e:
        return None, str(e)

if st.button("Generate Report"):
    with st.spinner(f"Fetching data for {ticker}..."):
        # Fetch stock data
        stock_data, stock_error = get_stock_data(ticker, start_date, end_date)
        if stock_error:
            st.error(f"Error fetching {ticker} data: {stock_error}")
        else:
            # Fetch benchmark data
            benchmark_data, bench_error = get_stock_data(benchmark, start_date, end_date)
            if bench_error:
                st.error(f"Error fetching benchmark data: {bench_error}")
            else:
                # Display data info
                st.info(f"Retrieved {len(stock_data)} data points for {ticker} and {len(benchmark_data)} for {benchmark}")
                
                # Align the data
                stock_data, benchmark_data = align_data(stock_data, benchmark_data)
                
                with st.spinner("Generating report..."):
                    # Generate the report
                    html_content, error = generate_quantstats_report(stock_data, benchmark_data, report_type)
                    
                    if error:
                        st.error(f"Error generating report: {error}")
                    elif html_content:
                        # Display the report directly
                        st.components.v1.html(html_content, height=800, scrolling=True)
                    else:
                        st.error("Failed to generate report content")

# Add information about the app
st.markdown("---")
st.markdown("""
### 📝 About This App
This app uses the following Python libraries:
- **QuantStats**: For generating comprehensive investment analytics and reports
- **yfinance**: For fetching financial data from Yahoo Finance
- **Streamlit**: For creating the web interface

### 💡 How to Use
1. Enter a valid stock/ETF symbol (e.g., AAPL, SPY, QQQ)
2. Select your desired date range
3. Choose a benchmark for comparison
4. Select the type of report you want to generate
5. Click 'Generate Report' to view the analysis

### ⚠️ Note
- Data is sourced from Yahoo Finance
- Some tickers might not be available or have limited data
- Generating detailed reports might take a few moments
""")

# Footer
st.markdown("---")
st.markdown("Created with ❤️ using Streamlit and QuantStats")
