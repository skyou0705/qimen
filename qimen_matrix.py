def get_dun_and_ju(jieqi, day_ganzhi):
    gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    jieqi_ju_map = {
        "冬至": ("陽", [1, 7, 4]), "小寒": ("陽", [2, 8, 5]), "大寒": ("陽", [3, 9, 6]),
        "立春": ("陽", [8, 5, 2]), "雨水": ("陽", [9, 6, 3]), "驚蟄": ("陽", [1, 7, 4]),
        "春分": ("陽", [3, 9, 6]), "清明": ("陽", [4, 1, 7]), "谷雨": ("陽", [5, 2, 8]),
        "立夏": ("陽", [4, 1, 7]), "小滿": ("陽", [5, 2, 8]), "芒種": ("陽", [6, 3, 9]),
        "夏至": ("陰", [9, 3, 6]), "小暑": ("陰", [8, 2, 5]), "大暑": ("陰", [7, 1, 4]),
        "立秋": ("陰", [2, 5, 8]), "處暑": ("陰", [1, 4, 7]), "白露": ("陰", [9, 3, 6]),
        "秋分": ("陰", [7, 1, 4]), "寒露": ("陰", [6, 9, 3]), "霜降": ("陰", [5, 8, 2]),
        "立冬": ("陰", [6, 9, 3]), "小雪": ("陰", [5, 8, 2]), "大雪": ("陰", [4, 7, 1])
    }
    jieqi = jieqi.replace("穀", "谷") 
    gan_idx = gan_list.index(day_ganzhi[0]); zhi_idx = zhi_list.index(day_ganzhi[1])
    diff = gan_idx % 5; fu_tou_zhi_idx = (zhi_idx - diff) % 12; rem = fu_tou_zhi_idx % 3
    yuan_idx = 0 if rem == 0 else (1 if rem == 2 else 2)
    dun_type, ju_list = jieqi_ju_map[jieqi]
    return dun_type, ju_list[yuan_idx]

def get_di_pan(dun_type, ju_num):
    qi_yi = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]
    di_pan = {}; step = 1 if dun_type == "陽" else -1
    current_palace = ju_num
    for item in qi_yi:
        di_pan[current_palace] = item
        current_palace += step
        if current_palace > 9: current_palace -= 9
        elif current_palace < 1: current_palace += 9
    return di_pan

def get_relation(my_wx, target_wx):
    if my_wx == target_wx: return "🤝 比和 (平穩)"
    relations = {
        "水": {"生":"木", "剋":"火", "被生":"金", "被剋":"土"},
        "火": {"生":"土", "剋":"金", "被生":"木", "被剋":"水"},
        "木": {"生":"火", "剋":"土", "被生":"水", "被剋":"金"},
        "金": {"生":"水", "剋":"木", "被生":"土", "被剋":"火"},
        "土": {"生":"金", "剋":"水", "被生":"火", "被剋":"木"}
    }
    if relations[my_wx]["生"] == target_wx: return "📤 我生 (耗損)"
    if relations[my_wx]["剋"] == target_wx: return "⚔️ 我剋 (掌控)"
    if relations[my_wx]["被生"] == target_wx: return "📥 生我 (獲利)"
    if relations[my_wx]["被剋"] == target_wx: return "💀 剋我 (風險)"

def generate_full_matrix(jieqi, day_ganzhi, time_ganzhi):
    gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    dun_type, ju_num = get_dun_and_ju(jieqi, day_ganzhi)
    di_pan = get_di_pan(dun_type, ju_num)
    t_gan, t_zhi = time_ganzhi[0], time_ganzhi[1]
    t_gan_idx, t_zhi_idx = gan_list.index(t_gan), zhi_list.index(t_zhi)
    diff = t_gan_idx
    xun_zhi_idx = (t_zhi_idx - diff) % 12
    xun_shou = f"甲{zhi_list[xun_zhi_idx]}"
    xun_yi_map = {"甲子":"戊", "甲戌":"己", "甲申":"庚", "甲午":"辛", "甲辰":"壬", "甲寅":"癸"}
    xun_yi = xun_yi_map[xun_shou]
    
    base_palace = next(p for p, g in di_pan.items() if g == xun_yi)
    star_rot = [1, 8, 3, 4, 9, 2, 7, 6]
    star_base = {1:"天蓬", 8:"天任", 3:"天沖", 4:"天輔", 9:"天英", 2:"天芮", 7:"天柱", 6:"天心", 5:"天禽"}
    door_base = {1:"休門", 8:"生門", 3:"傷門", 4:"杜門", 9:"景門", 2:"死門", 7:"驚門", 6:"開門", 5:"死門"}
    zf_star = star_base[base_palace if base_palace != 5 else 2]
    zs_door = door_base[base_palace if base_palace != 5 else 2]
    hour_gan_palace = next(p for p, g in di_pan.items() if g == t_gan) if t_gan != "甲" else ju_num
    if hour_gan_palace == 5: hour_gan_palace = 2
    
    star_pos = {}
    rot_idx_start = star_rot.index(base_palace if base_palace != 5 else 2)
    rot_idx_end = star_rot.index(hour_gan_palace)
    offset = (rot_idx_end - rot_idx_start) % 8
    for i, p in enumerate(star_rot):
        star_pos[star_rot[(i + offset) % 8]] = star_base[p]
    star_pos[5] = "--"
    
    tian_gan = {}
    for p in star_rot:
        orig_p = star_rot[(star_rot.index(p) - offset) % 8]
        tian_gan[p] = di_pan[orig_p]
    tian_gan[5] = "--"
    
    step_dist = (t_zhi_idx - xun_zhi_idx) % 12
    zs_pos = base_palace
    for _ in range(step_dist):
        if dun_type == "陽": zs_pos = zs_pos + 1 if zs_pos < 9 else 1
        else: zs_pos = zs_pos - 1 if zs_pos > 1 else 9
    door_rot = [1, 8, 3, 4, 9, 2, 7, 6]; door_pos = {}
    orig_zs_base = next(p for p, d in door_base.items() if d == zs_door)
    if orig_zs_base == 5: orig_zs_base = 2
    zs_start_idx = door_rot.index(orig_zs_base); zs_end_idx = door_rot.index(zs_pos if zs_pos != 5 else 2)
    door_offset = (zs_end_idx - zs_start_idx) % 8
    for i, p in enumerate(door_rot): door_pos[door_rot[(i + door_offset) % 8]] = door_base[p]
    door_pos[5] = "--"
    
    god_list = ["值符", "騰蛇", "太陰", "六合", "白虎", "玄武", "九地", "九天"]; god_pos = {}
    god_idx_start = star_rot.index(hour_gan_palace)
    for i in range(8):
        p = star_rot[(god_idx_start + (i if dun_type == "陽" else -i)) % 8]
        god_pos[p] = god_list[i]

    # --- 🚀 核心升級：馬星、門迫、擊刑演算法 ---
    ma_xing_map = {"申":"寅", "子":"寅", "辰":"寅", "寅":"申", "午":"申", "戌":"申", "亥":"巳", "卯":"巳", "未":"巳", "巳":"亥", "酉":"亥", "丑":"亥"}
    zhi_palace_map = {"子":1, "丑":8, "寅":8, "卯":3, "辰":4, "巳":4, "午":9, "未":2, "申":2, "酉":7, "戌":6, "亥":6}
    ma_palace = zhi_palace_map[ma_xing_map[t_zhi]]

    # 2. 板塊與本人定義
    wuxing_map = {1:"水", 2:"土", 3:"木", 4:"木", 5:"土", 6:"金", 7:"金", 8:"土", 9:"火"}
    sector_map = {9:"科技/AI", 1:"金融/流動", 3:"醫療/週期", 4:"綠能/消費", 7:"半導體/硬體", 6:"藍籌/軍工", 8:"地產/基建", 2:"價值/避險", 5:"市場中樞"}
    
    # 🌟 修復 Bug：當日干為「甲」時，找出它隱藏的六儀
    user_gan = day_ganzhi[0]
    if user_gan == "甲":
        # 如果日柱是甲子、甲戌等，直接用 xun_yi_map 轉換成對應的戊、己等
        user_gan = xun_yi_map.get(day_ganzhi, "戊") # 加上安全預設值
        
    user_palace = next(p for p, g in di_pan.items() if g == user_gan)
    user_wx = wuxing_map[user_palace]

    # 3. 遍歷九宮計算衝突
    matrix_data = {}
    alerts = []
    door_wx = {"休門":"水", "生門":"土", "傷門":"木", "杜門":"木", "景門":"火", "死門":"土", "驚門":"金", "開門":"金"}

    for i in range(1, 10):
        tg, dg, door = tian_gan.get(i, "--"), di_pan[i], door_pos.get(i, "--")
        is_ma = (i == ma_palace)
        is_jixing, is_menpo = False, False
        
        # 擊刑判定
        if (tg == "戊" and i == 3) or (tg == "己" and i == 2) or (tg == "庚" and i == 8) or \
           (tg == "辛" and i == 9) or (tg == "壬" and i == 4) or (tg == "癸" and i == 4): is_jixing = True

        # 門迫判定
        if door in door_wx:
            m_wx, p_wx = door_wx[door], wuxing_map[i]
            if (m_wx=="水" and p_wx=="火") or (m_wx=="火" and p_wx=="金") or \
               (m_wx=="金" and p_wx=="木") or (m_wx=="木" and p_wx=="土") or \
               (m_wx=="土" and p_wx=="水"): is_menpo = True

        # 寫入警報
        if is_jixing: alerts.append(f"⚡ 第 {i} 宮【擊刑】：資本耗損風險，嚴防洗盤。")
        if is_menpo: alerts.append(f"🚧 第 {i} 宮【門迫】：執行阻力大，小心假突破。")
        if is_ma: alerts.append(f"🐎 第 {i} 宮【馬星】：動能觸發位，波動率將激增。")

        matrix_data[i] = {
            "神": god_pos.get(i, "--"), "星": star_pos.get(i, "--"), "門": door,
            "天干": tg, "地干": dg, "板塊": sector_map[i], "本人": (i == user_palace),
            "關係": get_relation(user_wx, wuxing_map[i]),
            "馬星": is_ma, "擊刑": is_jixing, "門迫": is_menpo,
            "空亡": (i in [zhi_palace_map[z] for z in {"甲子":["戌","亥"],"甲戌":["申","酉"],"甲申":["午","未"],"甲午":["辰","巳"],"甲辰":["寅","卯"],"甲寅":["子","丑"]}[xun_shou]]),
            "危險": (tg == "戊" and dg == "庚") or (tg == "庚" and dg == "戊")
        }
    
    return {"遁法": dun_type, "局數": ju_num, "莊家情報": {"值符": zf_star, "值使": zs_door, "旬首": xun_shou}, "九宮格": matrix_data, "警報": alerts}
