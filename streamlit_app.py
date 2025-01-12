import streamlit as st
import yfinance as yf
import quantstats as qs
import os

def main():
    # Streamlit app title
    st.title("QuantStats Report Generator")

    # Input field for the stock/ETF ticker
    ticker = st.text_input("Enter the Stock/ETF ticker (Yahoo Finance):", "AAPL")

    # Input field for the start and end dates
    start_date = st.date_input("Start Date:", value=None)
    end_date = st.date_input("End Date:", value=None)

    # Button to generate report
    if st.button("Generate QuantStats Report"):
        if not ticker:
            st.error("Please enter a valid ticker.")
        elif not start_date or not end_date:
            st.error("Please select both start and end dates.")
        else:
            try:
                # Fetch historical stock data
                st.write(f"Fetching data for {ticker}...")
                data = yf.download(ticker, start=start_date, end=end_date)

                if data.empty:
                    st.error("No data found for the given ticker and date range.")
                else:
                    # Calculate daily returns
                    st.write("Calculating returns...")
                    returns = data["Adj Close"].pct_change().dropna()

                    # Generate QuantStats report
                    st.write("Generating QuantStats report...")

                    report_path = f"quantstats_report_{ticker}.html"
                    qs.reports.html(returns, output=report_path, title=f"QuantStats Report for {ticker}")

                    # Display link to download the report
                    st.success("Report generated successfully!")
                    with open(report_path, "rb") as file:
                        st.download_button(
                            label="Download QuantStats Report",
                            data=file,
                            file_name=f"QuantStats_Report_{ticker}.html",
                            mime="text/html",
                        )

                    # Show preview of the report in an iframe
                    st.write("Preview of the QuantStats Report:")
                    with open(report_path, "r") as f:
                        st.components.v1.html(f.read(), height=800, scrolling=True)

                    # Clean up the generated HTML file
                    os.remove(report_path)

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
