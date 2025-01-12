import streamlit as st
import yfinance as yf
import quantstats as qs
import pandas as pd
from datetime import datetime, timedelta
import tempfile
import os

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

if st.button("Generate Report"):
    try:
        with st.spinner(f"Fetching data and generating report for {ticker}..."):
            # Fetch data
            stock_data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False
            )['Adj Close']
            
            benchmark_data = yf.download(
                benchmark,
                start=start_date,
                end=end_date,
                progress=False
            )['Adj Close']
            
            # Create temporary directory for report
            with tempfile.TemporaryDirectory() as tmpdir:
                # Generate report based on selection
                if report_type == "Basic":
                    report_path = os.path.join(tmpdir, f"{ticker}_basic_report.html")
                    qs.reports.basic(
                        stock_data,
                        benchmark_data,
                        output=report_path
                    )
                elif report_type == "Full":
                    report_path = os.path.join(tmpdir, f"{ticker}_full_report.html")
                    qs.reports.full(
                        stock_data,
                        benchmark_data,
                        output=report_path
                    )
                else:  # Detailed
                    report_path = os.path.join(tmpdir, f"{ticker}_detailed_report.html")
                    qs.reports.html(
                        stock_data,
                        benchmark_data,
                        output=report_path
                    )
                
                # Read the generated report
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_html = f.read()
                
                # Display the report
                st.components.v1.html(report_html, height=800, scrolling=True)

    except Exception as e:
        st.error(f"Error occurred: {str(e)}")
        st.info("Please check if the ticker symbol is valid and try again.")

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
