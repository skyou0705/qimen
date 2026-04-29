import streamlit as st
import yfinance as yf
from datetime import datetime
from time_engine import get_qimen_time_params
from qimen_matrix import generate_full_matrix

st.set_page_config(page_title="奇門遁甲 金融儀表板", layout="wide")

if 'last_now' not in st.session_state: st.session_state.last_now = datetime.now()

# --- 側邊欄 ---
with st.sidebar:
    st.header("🕰️ 盤前推演控制器")
    use_custom_time = st.toggle("開啟手動回測模式", value=False)
    if use_custom_time:
        with st.form("time_form"):
            d = st.date_input("選擇日期", st.session_state.last_now.date())
            t = st.time_input("選擇時間", st.session_state.last_now.time())
            if st.form_submit_button("🚀 執行時空推演"): st.session_state.last_now = datetime.combine(d, t)
        now = st.session_state.last_now
    else: now = datetime.now()
    
    st.divider() # 分隔線
    
    # 🚀 新增：yfinance 個股 X 光機
    st.header("📈 個股 X 光機")
    st.caption("驗證奇門板塊與個股實體量能的共振狀態")
    ticker_input = st.text_input("輸入美股代號 (如 AAPL, NVDA, POET)", value="").upper()
    
    if ticker_input:
        with st.spinner("掃描量價數據中..."):
            try:
                stock = yf.Ticker(ticker_input)
                # 抓取近 5 天數據來計算動能
                hist = stock.history(period="5d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    pct_change = ((current_price - prev_close) / prev_close) * 100
                    
                    current_vol = hist['Volume'].iloc[-1]
                    avg_vol = hist['Volume'].mean()
                    vol_ratio = current_vol / avg_vol if avg_vol > 0 else 0
                    
                    # 顏色與動能判定
                    color = "#2ecc71" if pct_change >= 0 else "#e74c3c"
                    if vol_ratio > 1.3:
                        vol_status, vol_color = "🔥 動能爆發 (主升段警示)", "#e74c3c"
                    elif vol_ratio < 0.7:
                        vol_status, vol_color = "❄️ 量能枯竭 (虛假突破/盤整)", "#3498db"
                    else:
                        vol_status, vol_color = "📊 量能平穩 (跟隨大盤)", "#f1c40f"

                    st.markdown(f"""
                    <div style='background-color: #1a1a1a; padding: 12px; border-radius: 8px; border-left: 4px solid {color}; border-right: 1px solid #333; border-top: 1px solid #333; border-bottom: 1px solid #333;'>
                        <div style='font-size: 18px; font-weight: bold; color: #E0E0E0;'>{ticker_input}</div>
                        <div style='font-size: 26px; color: {color}; font-weight: bold; margin-bottom: 5px;'>${current_price:.2f} <span style='font-size: 14px;'>({pct_change:+.2f}%)</span></div>
                        <div style='font-size: 11px; color: #888;'>5日均量比: <span style='color: #ccc; font-weight: bold;'>{(vol_ratio*100):.0f}%</span></div>
                        <div style='font-size: 12px; color: {vol_color}; font-weight: bold; margin-top: 4px;'>{vol_status}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("⚠️ 找不到該股票數據，請確認代號是否正確。")
            except Exception as e:
                st.error("⚠️ 數據讀取失敗，可能是 API 限制或代號錯誤。")

time_params = get_qimen_time_params(now)
matrix_result = generate_full_matrix(time_params['當前節氣'], time_params['日柱'], time_params['時柱'])
info, palace_data = matrix_result['莊家情報'], matrix_result['九宮格']
center_rel = palace_data[5]['關係']

st.markdown("""
<div style="font-size: 20px; font-weight: bold; color: #E0E0E0; margin-bottom: 12px; margin-top: -20px;">
    🧮 奇門遁甲：時空演算法矩陣
</div>
""", unsafe_allow_html=True)

# 頂部 HUD
st.markdown(f"""
<style>
.hud-container {{ display: flex; justify-content: space-between; background-color: #1a1a1a; padding: 10px 15px; border-radius: 8px; border: 1px solid #333; margin-bottom: 12px; }}
.hud-item {{ text-align: center; flex: 1; border-right: 1px solid #333; }}
.hud-item:last-child {{ border-right: none; }}
.hud-label {{ font-size: 9px; color: #666; margin-bottom: 1px; }}
.hud-value {{ font-size: 14px; font-weight: bold; color: #ccc; }}
</style>
<div class="hud-container">
    <div class="hud-item"><div class="hud-label">真太陽時</div><div class="hud-value">{now.strftime("%H:%M")}</div></div>
    <div class="hud-item"><div class="hud-label">時空矩陣</div><div class="hud-value" style="color:#f1c40f">{matrix_result['遁法']}遁 {matrix_result['局數']} 局</div></div>
    <div class="hud-item"><div class="hud-label">本人(日)</div><div class="hud-value">{time_params['日柱']}</div></div>
    <div class="hud-item"><div class="hud-label">標的(時)</div><div class="hud-value">{time_params['時柱']}</div></div>
    <div class="hud-item"><div class="hud-label">值符</div><div class="hud-value" style="color:#e74c3c">{info['值符']}</div></div>
    <div class="hud-item"><div class="hud-label">值使</div><div class="hud-value" style="color:#2ecc71">{info['值使']}</div></div>
</div>
""", unsafe_allow_html=True)

# 🚀 左右平衡排版 (1.8 : 1)
col_left, col_right = st.columns([1.8, 1])

with col_left:
    st.markdown("""
    <style>
    .qimen-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; background-color: #111; padding: 8px; border-radius: 8px; }
    .palace-box { 
        background-color: #222; border: 1px solid #333; padding: 10px; border-radius: 4px; height: 160px; 
        position: relative; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden;
    }
    .top-header { display: flex; justify-content: space-between; align-items: center; width: 100%; margin-bottom: 2px; }
    .header-left { display: flex; align-items: center; flex-wrap: wrap; }
    .header-right { display: flex; align-items: center; white-space: nowrap; }
    .sector-tag { font-size: 11px; color: #5dade2; font-weight: bold; margin-bottom: 0; }
    .user-badge { background-color: #f1c40f; color: #000; font-size: 8px; padding: 1px 3px; border-radius: 2px; margin-left: 3px; }
    .rel-tag { font-size: 9px; padding: 2px 5px; border-radius: 3px; font-weight: bold; margin-left: 5px; }
    .status-bar { display: flex; flex-wrap: wrap; gap: 3px; width: 100%; justify-content: flex-start; margin-bottom: 6px; }
    .status-icon { font-size: 9px; padding: 0 2px; border-radius: 2px; border: 1px solid currentColor; margin-left: 0; }
    
    .palace-box.danger { border: 1px solid #e74c3c; box-shadow: inset 0 0 5px rgba(231,76,60,0.2); }
    .palace-box.kongwang { opacity: 0.35; }
    .palace-box.center-core { border: 2px dashed #f1c40f; background: radial-gradient(circle, #2a2a2a 0%, #1a1a1a 100%); }
    .rel-profit { background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; border: 1px solid #2ecc71; }
    .rel-risk { background-color: rgba(231, 76, 60, 0.2); color: #e74c3c; border: 1px solid #e74c3c; }
    .rel-ctrl { background-color: rgba(241, 196, 15, 0.2); color: #f1c40f; border: 1px solid #f1c40f; }
    .rel-flat { background-color: rgba(149, 165, 166, 0.2); color: #95a5a6; border: 1px solid #95a5a6; }
    
    .row-1 { display: flex; justify-content: space-between; color: #888; font-size: 11px; margin-top: 0; }
    .row-2 { text-align: center; font-size: 24px; font-weight: bold; color: #f1c40f; margin: 2px 0; }
    .row-3 { display: flex; justify-content: center; gap: 6px; font-size: 18px; font-weight: bold; }
    .p-num { text-align: right; font-size: 9px; color: #333; position: absolute; bottom: 4px; right: 8px; }
    </style>
    """, unsafe_allow_html=True)

    luoshu_order, html = [4, 9, 2, 3, 5, 7, 8, 1, 6], '<div class="qimen-grid">\n'
    for p in luoshu_order:
        d = palace_data[p]
        css = f"palace-box {'danger' if d['危險'] else ''} {'kongwang' if d['空亡'] else ''} {'center-core' if p==5 else ''}"
        
        icons_html = ""
        if d['馬星']: icons_html += '<span class="status-icon" style="color:#5dade2; border-color:#5dade2;">🐎馬</span>'
        if d['擊刑']: icons_html += '<span class="status-icon" style="color:#e74c3c; border-color:#e74c3c;">⚡刑</span>'
        if d['門迫']: icons_html += '<span class="status-icon" style="color:#f39c12; border-color:#f39c12;">🚧迫</span>'
        if d['空亡']: icons_html += '<span class="status-icon" style="color:#777; border-color:#777;">空</span>'
        status_bar_html = f'<div class="status-bar">{icons_html}</div>'

        rel_class = "rel-profit" if "生我" in d['關係'] else "rel-risk" if "剋我" in d['關係'] else "rel-ctrl" if "我剋" in d['關係'] else "rel-flat"
        rel_html = f'<div class="rel-tag {rel_class}">{d["關係"] if not d["本人"] else "📍座標"}</div>'

        if p == 5:
            html += f"""<div class="{css}">
<div class="top-header"><div class="header-left"><div class="sector-tag">🌐 市場中樞</div></div><div class="header-right"><div class="rel-tag rel-flat">{d['關係']}</div></div></div>
<div style="text-align:center; color:#555; font-size:10px; margin-top:30px;">MACRO INDEX</div>
<div class="p-num">5宮</div>
</div>\n"""
        else:
            html += f"""<div class="{css}">
<div class="top-header"><div class="header-left"><div class="sector-tag">{d['板塊']}{'<span class="user-badge">本人</span>' if d['本人'] else ''}</div></div><div class="header-right">{rel_html}</div></div>
{status_bar_html}
<div class="row-1"><span>{d['神']}</span><span>{d['星']}</span></div>
<div class="row-2">{d['門']}</div>
<div class="row-3"><span style="color:#e74c3c">{d['天干']}</span><span style="color:#555">/</span><span style="color:#2ecc71">{d['地干']}</span></div>
<div class="p-num">{p}宮</div>
</div>\n"""
    st.markdown(html + '</div>', unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <style>
    .right-panel { background-color: #1a1a1a; padding: 12px; border-radius: 8px; border: 1px solid #333; height: 100%; }
    .section-title { font-size: 13px; font-weight: bold; color: #888; margin-bottom: 10px; border-left: 4px solid #f1c40f; padding-left: 10px; }
    .insight-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .insight-item { font-size: 11px; padding: 10px; background: #262626; border: 1px solid #333; border-radius: 5px; min-height: 60px; display: flex; flex-direction: column; justify-content: center; }
    .insight-label { color: #5dade2; font-weight: bold; margin-bottom: 2px; font-size: 12px; }
    .macro-alert { font-size: 12px; font-weight: bold; padding: 10px; border-radius: 5px; border: 1px solid #e74c3c; color: #e74c3c; background: rgba(231,76,60,0.05); margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)
    
    if "剋我" in center_rel: st.markdown(f'<div class="macro-alert">🚨 大盤逆風：{center_rel}，建議縮減部位或觀望。</div>', unsafe_allow_html=True)
    elif "生我" in center_rel: st.markdown(f'<div class="macro-alert" style="color:#2ecc71; border-color:#2ecc71; background:rgba(46,204,113,0.05)">🚀 大盤環境順風：{center_rel}，積極尋找獲利機會。</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="border-left-color:#e74c3c">📉 系統日誌</div>', unsafe_allow_html=True)
    if matrix_result['警報']:
        for alert in matrix_result['警報'][:3]:
            st.markdown(f'<div style="font-size:10px; color:#aaa; margin-bottom:3px; padding-left:5px; border-left:2px solid #444;">{alert}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:10px; color:#2ecc71; padding-left:5px;">結構穩定，無即時預警。</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top: 20px;">🧭 板塊決策雷達 (2x3 Grid)</div>', unsafe_allow_html=True)
    insight_html = '<div class="insight-grid">'
    for p_num, d in palace_data.items():
        if p_num != 5 and not d['本人']:
            insight_html += f'<div class="insight-item"><div class="insight-label">{d["板塊"]}</div>{d["關係"]}</div>'
    st.markdown(insight_html + '</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
