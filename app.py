import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

# ===== TITLE =====
st.title("📊 Stock Analysis Dashboard")

# ===== INPUT =====
tickers_input = st.text_input("Enter Tickers (comma separated)", "TCS,ICICIBANK")
tickers = [t.strip().upper() for t in tickers_input.split(",")]

days = st.slider("Select number of days", 30, 365, 180)

today = datetime.today()
start_date = today - timedelta(days=days)
end_date = today

# ===== ANALYSIS BUTTON =====
if st.button("Analyze Stocks"):

    st.subheader("📊 Individual Stock Analysis")

    for ticker in tickers:
        st.markdown(f"### {ticker}")

        data = yf.download(f"{ticker}.NS", start=start_date, end=end_date, progress=False)

        if data.empty:
            st.warning(f"No data for {ticker}")
            continue

        data.columns = data.columns.get_level_values(0)

        start_price = data['Close'].iloc[0]
        end_price = data['Close'].iloc[-1]

        change = end_price - start_price
        pct = (change / start_price) * 100

        max_price = data['High'].max()
        min_price = data['Low'].min()

        max_date = data['High'].idxmax()
        min_date = data['Low'].idxmin()

        # ===== METRICS =====
        col1, col2, col3 = st.columns(3)

        col1.metric("Start Price", f"₹{start_price:.2f}")
        col2.metric("End Price", f"₹{end_price:.2f}")
        col3.metric("Return", f"{pct:.2f}%")

        st.write(f"📈 High: ₹{max_price:.2f} on {max_date.strftime('%Y-%m-%d')}")
        st.write(f"📉 Low: ₹{min_price:.2f} on {min_date.strftime('%Y-%m-%d')}")

        # ===== INTERACTIVE CHART =====
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name='Close Price'
        ))

        fig.add_trace(go.Scatter(
            x=[max_date],
            y=[max_price],
            mode='markers+text',
            name='High',
            text=[f"High ₹{max_price:.2f}"],
            textposition="top center"
        ))

        fig.add_trace(go.Scatter(
            x=[min_date],
            y=[min_price],
            mode='markers+text',
            name='Low',
            text=[f"Low ₹{min_price:.2f}"],
            textposition="bottom center"
        ))

        fig.update_layout(
            title=f"{ticker} Price Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

    # ===== COMPARISON =====
    st.subheader("📊 Stock Comparison (Normalized)")

    fig = go.Figure()

    for ticker in tickers:
        data = yf.download(f"{ticker}.NS", start=start_date, end=end_date, progress=False)

        if data.empty:
            continue

        data.columns = data.columns.get_level_values(0)

        normalized = (data['Close'] / data['Close'].iloc[0]) * 100

        fig.add_trace(go.Scatter(
            x=data.index,
            y=normalized,
            mode='lines',
            name=ticker
        ))

    fig.update_layout(
        title="Stock Comparison (Base = 100)",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)