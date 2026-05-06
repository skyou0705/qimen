import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# ==========================================
# 網頁版面設定
# ==========================================
st.set_page_config(page_title="LC Capital 雷達", layout="wide")
st.title("🦅 LC Capital 籌碼雷達系統 v1.0")

# 【修改點 1】：預設留白 (value="")
target_ticker = st.text_input("輸入要掃描的股票代碼 (例如: SOUN, LUMN, NVDA):", value="").upper()

if st.button("啟動深度掃描"):
    # 【修改點 2】：防呆機制，如果沒輸入代碼就擋下來
    if not target_ticker:
        st.warning("⚠️ 首席，請先輸入股票代碼！")
    else:
        with st.spinner(f"正在駭入 {target_ticker} 的底層數據庫..."):
            try:
                # 【修改點 3】：加入偽裝面具 (User-Agent)，破解 Yahoo 的 Rate Limit 封鎖
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                # 將偽裝好的 session 交給 yfinance
                stock = yf.Ticker(target_ticker, session=session)
                
                col1, col2 = st.columns(2)
                
                # 左半邊：基礎 K 線與量能
                with col1:
                    st.subheader("📊 近 5 日量價表現")
                    hist = stock.history(period="5d")
                    
                    if not hist.empty:
                        # 把日期調整得漂亮一點
                        hist.index = hist.index.strftime('%Y-%m-%d')
                        st.dataframe(hist[['Close', 'Volume']], use_container_width=True)
                        st.line_chart(hist['Close']) 
                    else:
                        st.warning("抓不到歷史數據，可能是代碼錯誤，或 Yahoo 依然在阻擋連線。")

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
                        top_calls = top_calls[['strike', 'lastPrice', 'volume', 'openInterest']]
                        top_calls.columns = ['履約價 (Strike)', '最新價', '成交量 (Vol)', '未平倉 (OI)']
                        
                        st.dataframe(top_calls, hide_index=True, use_container_width=True)
                    else:
                        st.warning("⚠️ 該股票目前沒有可用的期權數據。")
                        
            # 【修改點 4】：優雅的錯誤捕捉，不要再讓醜陋的紅字佔滿螢幕
            except Exception as e:
                st.error("連線遭拒或發生未知的數據錯誤！")
                st.info("💡 實戰情報：Yahoo Finance 偶爾會嚴格封鎖雲端主機 (Streamlit Cloud) 的 IP。如果持續報錯，請稍等幾分鐘後重試，或者在本地端 (本機電腦) 執行此看板。")
