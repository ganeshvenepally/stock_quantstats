import streamlit as st
import yfinance as yf
import quantstats as qs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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

def download_stock_data(ticker, start_date, end_date):
    """Download stock data using yfinance and convert to returns"""
    try:
        # Download data using yfinance
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if df.empty:
            return None, f"No data found for {ticker}"
        
        # Calculate returns from Adj Close prices
        returns = df['Adj Close'].pct_change()
        returns = returns.dropna()
        
        # Convert index timezone to UTC and then remove timezone info
        if returns.index.tz is not None:
            returns.index = returns.index.tz_convert('UTC').tz_localize(None)
        
        return returns, None
            
    except Exception as e:
        return None, str(e)

def generate_basic_report(returns, benchmark_returns):
    """Generate basic metrics report"""
    try:
        metrics = pd.DataFrame(columns=['Metric', 'Value'])
        
        # Calculate basic metrics using QuantStats
        metrics.loc[len(metrics)] = ['Total Return', f"{qs.stats.comp(returns):.2%}"]
        metrics.loc[len(metrics)] = ['Annual Volatility', f"{qs.stats.volatility(returns):.2%}"]
        metrics.loc[len(metrics)] = ['Sharpe Ratio', f"{qs.stats.sharpe(returns):.2f}"]
        metrics.loc[len(metrics)] = ['Max Drawdown', f"{qs.stats.max_drawdown(returns):.2%}"]
        metrics.loc[len(metrics)] = ['Win Rate', f"{qs.stats.win_rate(returns):.2%}"]
        metrics.loc[len(metrics)] = ['Risk of Ruin', f"{qs.stats.risk_of_ruin(returns):.2%}"]
        metrics.loc[len(metrics)] = ['Value at Risk', f"{qs.stats.var(returns):.2%}"]
        metrics.loc[len(metrics)] = ['Expected Return (Monthly)', f"{qs.stats.expected_return(returns):.2%}"]
        
        # Convert to HTML
        html = f"""
        <div style='padding: 20px'>
            <h2>Basic Performance Report for {ticker}</h2>
            {metrics.to_html(index=False, escape=False, classes='table table-striped')}
        </div>
        """
        return html
        
    except Exception as e:
        raise Exception(f"Error generating basic report: {str(e)}")

def generate_quantstats_report(returns, benchmark_returns, report_type):
    """Generate QuantStats report and return HTML content"""
    try:
        from io import StringIO
        output = StringIO()
        
        if report_type == "Basic":
            return generate_basic_report(returns, benchmark_returns)
        elif report_type == "Full":
            qs.reports.full(returns, benchmark_returns, output=output)
            content = output.getvalue()
            output.close()
            return content
        else:  # Detailed
            qs.reports.html(returns, benchmark_returns, output=output)
            content = output.getvalue()
            output.close()
            return content
            
    except Exception as e:
        raise Exception(f"Error generating report: {str(e)}")

if st.button("Generate Report"):
    with st.spinner(f"Fetching data for {ticker}..."):
        # Fetch stock data
        stock_returns, stock_error = download_stock_data(ticker, start_date, end_date)
        if stock_error:
            st.error(f"Error fetching {ticker} data: {stock_error}")
        else:
            # Fetch benchmark data
            benchmark_returns, bench_error = download_stock_data(benchmark, start_date, end_date)
            if bench_error:
                st.error(f"Error fetching benchmark data: {bench_error}")
            else:
                # Display data info
                st.info(f"Retrieved {len(stock_returns)} data points for {ticker} and {len(benchmark_returns)} for {benchmark}")
                
                with st.spinner("Generating report..."):
                    try:
                        # Generate the report
                        html_content = generate_quantstats_report(stock_returns, benchmark_returns, report_type)
                        
                        if html_content:
                            # Display the report
                            st.components.v1.html(html_content, height=800, scrolling=True)
                        else:
                            st.error("Failed to generate report content")
                    except Exception as e:
                        st.error(f"Error generating report: {str(e)}")

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
