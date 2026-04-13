
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import plotly.subplots as sp


st.title("📊 Stock Analysis Dashboard")


tickers_input = st.text_input("Enter Tickers (comma separated)", "TCS,ICICIBANK")
tickers = [t.strip().upper() for t in tickers_input.split(",")]

days = st.slider("Select number of days", 30, 365, 180)

today = datetime.today()
start_date = today - timedelta(days=days)
end_date = today


if st.button("Analyze Stocks"):

    for ticker in tickers:
        st.subheader(f"📊 {ticker}")

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

        col1, col2, col3 = st.columns(3)
        col1.metric("Start Price", f"₹{start_price:.2f}")
        col2.metric("End Price", f"₹{end_price:.2f}")
        col3.metric("Return", f"{pct:.2f}%")

        st.write(f"📈 High: ₹{max_price:.2f} on {max_date.strftime('%Y-%m-%d')}")
        st.write(f"📉 Low: ₹{min_price:.2f} on {min_date.strftime('%Y-%m-%d')}")


        fig_price = go.Figure()

        fig_price.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name='Close Price'
        ))

        fig_price.update_layout(
            title=f"{ticker} Price Chart",
            hovermode="x unified"
        )

        st.plotly_chart(fig_price, use_container_width=True)


        data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
        data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()

        data['MACD'] = data['EMA_12'] - data['EMA_26']
        data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        data['Histogram'] = data['MACD'] - data['Signal']

        data['Buy'] = (data['MACD'] > data['Signal']) & (data['MACD'].shift(1) <= data['Signal'].shift(1))
        data['Sell'] = (data['MACD'] < data['Signal']) & (data['MACD'].shift(1) >= data['Signal'].shift(1))


        fig = sp.make_subplots(rows=2, cols=1, shared_xaxes=True,
                               row_heights=[0.6, 0.4])


        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name='Close'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=data[data['Buy']].index,
            y=data[data['Buy']]['Close'],
            mode='markers',
            marker=dict(symbol='triangle-up', size=10),
            name='Buy'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=data[data['Sell']].index,
            y=data[data['Sell']]['Close'],
            mode='markers',
            marker=dict(symbol='triangle-down', size=10),
            name='Sell'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MACD'],
            mode='lines',
            name='MACD'
        ), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Signal'],
            mode='lines',
            name='Signal'
        ), row=2, col=1)

        fig.add_trace(go.Bar(
            x=data.index,
            y=data['Histogram'],
            name='Histogram'
        ), row=2, col=1)

        fig.update_layout(
            title=f"{ticker} MACD Strategy",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        nifty50 = yf.download("^NSEI", start=start_date, end=end_date, progress=False)
        nifty100 = yf.download("^CNX100", start=start_date, end=end_date, progress=False)

        if not nifty50.empty:
            nifty50.columns = nifty50.columns.get_level_values(0)

        if not nifty100.empty:
            nifty100.columns = nifty100.columns.get_level_values(0)


        fig_price = go.Figure()

        fig_price.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name=ticker
        ))


        if not nifty50.empty:
            fig_price.add_trace(go.Scatter(
                x=nifty50.index,
                y=nifty50['Close'],
                mode='lines',
                name='NIFTY 50',
                line=dict(dash='dash')
            ))


        if not nifty100.empty:
            fig_price.add_trace(go.Scatter(
                x=nifty100.index,
                y=nifty100['Close'],
                mode='lines',
                name='NIFTY 100',
                line=dict(dash='dot')
            ))

        fig_price.update_layout(
            title=f"{ticker} vs NIFTY 50 & NIFTY 100",
            hovermode="x unified"
        )

        st.plotly_chart(fig_price, use_container_width=True)
        stock_return = pct

        if not nifty50.empty:
            nifty_return = ((nifty50['Close'].iloc[-1] - nifty50['Close'].iloc[0]) / nifty50['Close'].iloc[0]) * 100

            if stock_return > nifty_return:
                st.success("Outperforming NIFTY 50 ✅")
            else:
                st.error("Underperforming NIFTY 50 ❌")

        summary_data = []
        summary_data.append({
            "Ticker": ticker,
            "Start Price": round(start_price, 2),
            "End Price": round(end_price, 2),
            "Return %": round(pct, 2)
        })

