import streamlit as st
import yfinance as yf
import pandas as pd

# ==========================================
# 網頁版面設定
# ==========================================
st.set_page_config(page_title="LC Capital 雷達", layout="wide")
st.title("🦅 LC Capital 籌碼雷達系統 v1.0")

target_ticker = st.text_input("輸入要掃描的股票代碼 (例如: MARA, LUMN, NVDA):", value="MARA").upper()

if st.button("啟動深度掃描"):
    with st.spinner(f"正在駭入 {target_ticker} 的底層數據庫..."):
        stock = yf.Ticker(target_ticker)
        
        col1, col2 = st.columns(2)
        
        # 左半邊：基礎 K 線與量能
        with col1:
            st.subheader("📊 近 5 日量價表現")
            hist = stock.history(period="5d")
            if not hist.empty:
                # 把日期調整得漂亮一點
                hist.index = hist.index.strftime('%Y-%m-%d')
                st.dataframe(hist[['Close', 'Volume']], use_container_width=True)
                st.line_chart(hist['Close']) # 直接畫出走勢圖
            else:
                st.warning("抓不到這檔股票的歷史數據，請確認代碼是否正確。")

        # 右半邊：期權異常掃描
        with col2:
            st.subheader("🔥 聰明錢足跡 (Call 異常大單)")
            options_dates = stock.options
            
            if options_dates:
                nearest_date = options_dates[0]
                st.info(f"最近結算日: {nearest_date}")
                
                opt_chain = stock.option_chain(nearest_date)
                calls = opt_chain.calls
                
                # 篩選並排序
                top_calls = calls.sort_values(by='volume', ascending=False).head(5)
                # 重新命名欄位讓它更直觀
                top_calls = top_calls[['strike', 'lastPrice', 'volume', 'openInterest']]
                top_calls.columns = ['履約價 (Strike)', '最新價', '成交量 (Vol)', '未平倉 (OI)']
                
                st.dataframe(top_calls, hide_index=True, use_container_width=True)
            else:
                st.warning("⚠️ 該股票目前沒有可用的期權數據。")
