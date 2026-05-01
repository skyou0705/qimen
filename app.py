import streamlit as st
import yfinance as yf
from datetime import datetime
import os
from time_engine import get_qimen_time_params
from qimen_matrix import generate_full_matrix

# ==========================================
# 頁面基本設定與快取引擎
# ==========================================
st.set_page_config(page_title="奇門遁甲 金融儀表板", layout="wide")

if 'last_now' not in st.session_state: 
    st.session_state.last_now = datetime.now()

@st.cache_data(ttl=60, show_spinner=False)
def fetch_stock_data(ticker):
    """取得 yfinance 數據並快取 60 秒，避免切換時間時卡頓或被鎖 IP"""
    stock = yf.Ticker(ticker)
    return stock.history(period="5d")

def write_snapshot_to_log(filename, content):
    """寫入日誌的底層邏輯：採用 utf-8 與 a (追加) 模式"""
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(content + "\n" + "-"*50 + "\n")
        return True
    except Exception as e:
        st.error(f"寫入失敗：{e}")
        return False

# ==========================================
# 側邊欄：控制器與 X 光機
# ==========================================
with st.sidebar:
    st.header("🕰️ 盤前推演控制器")
    use_custom_time_state = st.toggle("開啟手動回測模式", value=False)
    
    if use_custom_time_state:
        d = st.date_input("選擇日期", st.session_state.last_now.date())
        t = st.time_input("選擇時間", st.session_state.last_now.time())
        
        # 🚀 全自動即時反應模式
        new_dt = datetime.combine(d, t)
        if new_dt != st.session_state.last_now:
            st.session_state.last_now = new_dt
            st.rerun()
            
        now = st.session_state.last_now
    else:
        now = datetime.now()
                
    st.divider()
    
    st.header("📈 個股 X 光機")
    st.caption("驗證奇門板塊與個股實體量能的共振狀態")
    
    ticker_input = st.text_input("輸入美股代號 (如 AAPL, NVDA, POET)", key="target_ticker").upper()
    
    if ticker_input:
        with st.spinner("掃描即時量價數據中..."):
            try:
                hist = fetch_stock_data(ticker_input)
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    pct_change = ((current_price - prev_close) / prev_close) * 100
                    
                    current_vol = hist['Volume'].iloc[-1]
                    avg_vol = hist['Volume'].mean()
                    vol_ratio = current_vol / avg_vol if avg_vol > 0 else 0
                    
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

                    # 📓 一鍵寫入 TXT 復盤日誌模組
                    st.write("") 
                    if st.button("📓 紀錄當前時空快照", use_container_width=True):
                        temp_params = get_qimen_time_params(now)
                        temp_matrix = generate_full_matrix(temp_params['當前節氣'], temp_params['日柱'], temp_params['時柱'])
                        
                        log_entry = (
                            f"【時空快照】 {now.strftime('%Y-%m-%d %H:%M:%S')} ({temp_params['時柱'][1]}時)\n"
                            f"► 矩陣: {temp_matrix['遁法']}遁{temp_matrix['局數']}局 | 值符: {temp_matrix['莊家情報']['值符']} | 值使: {temp_matrix['莊家情報']['值使']}\n"
                            f"► 標的: {ticker_input} | 價格: ${current_price:.2f} ({pct_change:+.2f}%)\n"
                            f"► 動能: {vol_status} (均量比 {vol_ratio*100:.0f}%)\n"
                            f"► 大盤中樞關係: {temp_matrix['九宮格'][5]['關係']}"
                        )
                        
                        if write_snapshot_to_log("trading_diary.txt", log_entry):
                            st.toast("✅ 數據已寫入 trading_diary.txt", icon="📝")
                else:
                    st.error("⚠️ 找不到該股票數據。")
            except Exception as e:
                st.error("⚠️ 數據讀取失敗，可能是 API 限制或代號錯誤。")

# ==========================================
# 奇門遁甲矩陣運算 (主畫面)
# ==========================================
time_params = get_qimen_time_params(now)
matrix_result = generate_full_matrix(time_params['當前節氣'], time_params['日柱'], time_params['時柱'])
info, palace_data = matrix_result['莊家情報'], matrix_result['九宮格']
center_rel = palace_data[5]['關係']
shichen_name = time_params['時柱'][1] + "時"

# ==========================================
# 主視覺佈局與 HUD 面板
# ==========================================
st.markdown("""
<div style="font-size: 20px; font-weight: bold; color: #E0E0E0; margin-bottom: 12px; margin-top: -20px;">
    🧮 奇門遁甲：時空演算法矩陣
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<style>
.hud-container {{ display: flex; justify-content: space-between; background-color: #1a1a1a; padding: 10px 15px; border-radius: 8px; border: 1px solid #333; margin-bottom: 12px; }}
.hud-item {{ text-align: center; flex: 1; border-right: 1px solid #333; }}
.hud-item:last-child {{ border-right: none; }}
.hud-label {{ font-size: 9px; color: #666; margin-bottom: 1px; }}
.hud-value {{ font-size: 14px; font-weight: bold; color: #ccc; }}
</style>
<div class="hud-container">
    <div class="hud-item"><div class="hud-label">真太陽時</div><div class="hud-value">{now.strftime("%H:%M")} <span style="font-size: 11px; color: #f1c40f; font-weight: normal;">({shichen_name})</span></div></div>
    <div class="hud-item"><div class="hud-label">時空矩陣</div><div class="hud-value" style="color:#f1c40f">{matrix_result['遁法']}遁 {matrix_result['局數']} 局</div></div>
    <div class="hud-item"><div class="hud-label">本人(日)</div><div class="hud-value">{time_params['日柱']}</div></div>
    <div class="hud-item"><div class="hud-label">標的(時)</div><div class="hud-value">{time_params['時柱']}</div></div>
    <div class="hud-item"><div class="hud-label">值符</div><div class="hud-value" style="color:#e74c3c">{info['值符']}</div></div>
    <div class="hud-item"><div class="hud-label">值使</div><div class="hud-value" style="color:#2ecc71">{info['值使']}</div></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 左右平衡排版 (1.8 : 1)
# ==========================================
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
    .sector-tag { font-size: 11px; color: #5dade2; font-weight: bold; margin-bottom: 0; white-space: nowrap; }
    .user-badge { background-color: #f1c40f; color: #000; font-size: 8px; padding: 1px 3px; border-radius: 2px; margin-left: 3px; }
    .rel-tag { font-size: 9px; padding: 2px 5px; border-radius: 3px; font-weight: bold; margin-left: 5px; white-space: nowrap; }
    .status-bar { display: flex; flex-wrap: wrap; gap: 3px; width: 100%; justify-content: flex-start; margin-bottom: 6px; }
    .status-icon { font-size: 9px; padding: 0 2px; border-radius: 2px; border: 1px solid currentColor; margin-left: 0; white-space: nowrap; }
    
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

    # ==========================================
    # 🤖 自動白話文翻譯引擎 (折疊面板)
    # ==========================================
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True) 
    
    QIMEN_DICT = {
        "神": {
            "值符": "主力大資本 (護盤力量)：最安全的跟隨信號，大機構重倉。",
            "騰蛇": "虛假與震盪 (高波動)：走勢上沖下洗，容易出現騙線或假突破。",
            "太陰": "暗盤與隱蔽 (潛伏期)：主力悄悄吸籌或出貨，成交量可能不明顯。",
            "六合": "併購與平穩 (合作)：走勢溫和，可能有合作、併購等利好消息。",
            "白虎": "暴漲暴跌 (高壓)：動能極強，伴隨極大風險，不是大賺就是大賠。",
            "玄武": "投機與假消息 (洗盤)：充滿投機熱錢，注意防範割韭菜陷阱。",
            "九地": "底部與盤整 (長線)：股價處於低位或長期橫盤，適合長線耐心佈局。",
            "九天": "主升段與泡沫 (新高)：股價不斷創新高，FOMO情緒狂熱，隨時準備見頂。"
        },
        "星": {
            "天蓬": "高風險大波動：容易大起大落的妖股，風險偏好極高。",
            "天任": "穩健慢牛：基本面良好的價值股，走勢緩慢但堅實。",
            "天沖": "動能突破 (軋空)：直線飆升，速度極快，但不持久。",
            "天輔": "穩步向上：有實質利好消息支撐，走勢健康。",
            "天英": "情緒化高熱度：市場焦點，但也容易「見光死」。",
            "天芮": "問題股與套牢：基本面有瑕疵，或上方有沉重套牢賣壓。",
            "天柱": "突發利空破壞：容易遇到破壞性的突發壞消息，小心閃崩。",
            "天心": "核心權重資產：板塊內的龍頭股，受管理層或政策影響大。"
        },
        "門": {
            "休門": "觀望與盤整：資金正在休息，適合觀望，不宜激進。",
            "生門": "絕對利潤 (多頭)：資金持續流入，有實質獲利空間，強烈看多。",
            "傷門": "激烈競爭與耗損：板塊內鬥嚴重，或容易產生虧損。",
            "杜門": "隱藏與停滯：方向不明朗，資金卡住不動，適合掛低單潛伏。",
            "景門": "消息面驅動：利好滿天飛，高點即將出現，適合獲利了結。",
            "死門": "資金死水：毫無流動性，基本面惡化，絕對避開。",
            "驚門": "恐慌與拋售：市場出現驚嚇，容易引發恐慌性殺跌。",
            "開門": "突破與順暢：阻力打開，事業開展順利，適合進場。"
        },
        "干": {
            "乙": "散戶資金/猶豫震盪",
            "丙": "熱錢/極端暴漲暴跌",
            "丁": "精準小資金/奇蹟點位",
            "戊": "主力大本金/市場基石",
            "己": "陷阱/泥沼陰跌",
            "庚": "強大阻力/破壞力量",
            "辛": "錯誤決策/套牢小損",
            "壬": "高頻量化/大起大落",
            "癸": "天網/流動性枯竭"
        }
    }

    with st.expander("🤖 深度解析：各板塊底層邏輯 (點擊展開)", expanded=False):
        for p in [8, 3, 4, 1, 9, 2, 6, 7]: # 排除中宮5
            d = palace_data[p]
            if d['空亡']:
                continue # 空亡的板塊直接跳過不顯示
                
            # 設定左側邊框顏色 (生我: 綠, 剋我: 紅, 其他: 黃)
            border_color = '#2ecc71' if '生我' in d['關係'] else '#e74c3c' if '剋我' in d['關係'] else '#f1c40f'
            
            st.markdown(f"""
            <div style="background-color: #1e1e1e; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid {border_color};">
                <div style="font-size: 14px; font-weight: bold; color: #5dade2; margin-bottom: 5px;">
                    {p}宮 - {d['板塊']} <span style="font-size:12px; color:#aaa; font-weight:normal;">({d['關係']})</span> {'<span style="color:#f1c40f;font-size:12px;">[📍本人坐標]</span>' if d['本人'] else ''}
                </div>
                <div style="font-size: 12px; color: #ccc; line-height: 1.6;">
                    <span style="color: #aaa;">[{d['神']}]</span> {QIMEN_DICT['神'].get(d['神'], '未知')}<br>
                    <span style="color: #aaa;">[{d['星']}]</span> {QIMEN_DICT['星'].get(d['星'], '未知')}<br>
                    <span style="color: #aaa;">[{d['門']}]</span> {QIMEN_DICT['門'].get(d['門'], '未知')}<br>
                    <span style="color: #aaa;">[{d['天干']}/{d['地干']}]</span> 天盤 {QIMEN_DICT['干'].get(d['天干'], '')} 遇上 地盤 {QIMEN_DICT['干'].get(d['地干'], '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

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

    st.markdown('<div class="section-title" style="margin-top: 20px;">🧭 板塊資金流向雷達</div>', unsafe_allow_html=True)
    insight_html = '<div class="insight-grid">'
    for p_num, d in palace_data.items():
        if p_num != 5 and not d['本人']:
            insight_html += f'<div class="insight-item"><div class="insight-label">{d["板塊"]}</div>{d["關係"]}</div>'
    st.markdown(insight_html + '</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
