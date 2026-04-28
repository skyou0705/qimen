from lunar_python import Solar, Lunar, EightChar
from datetime import datetime

def get_qimen_time_params(dt_obj):
    """
    奇門遁甲底層時間引擎
    輸入：標準的 datetime 物件
    輸出：包含四柱干支、當前節氣的精準字典
    """
    # 1. 將 Python 的 datetime 轉換為 lunar_python 的 Solar 物件
    solar = Solar.fromYmdHms(
        dt_obj.year, dt_obj.month, dt_obj.day, 
        dt_obj.hour, dt_obj.minute, dt_obj.second
    )
    
    # 2. 轉換為農曆物件 (底層會自動處理天文曆法)
    lunar = solar.getLunar()
    
    # 3. 獲取精準的八字四柱
    # lunar_python 的 getEightChar() 會自動根據交節氣的「分秒」來決定年月干支，非常精準
    ba_zi = lunar.getEightChar()
    
    # 提取干支
    year_ganzhi = ba_zi.getYear()
    month_ganzhi = ba_zi.getMonth()
    day_ganzhi = ba_zi.getDay()
    time_ganzhi = ba_zi.getTime()
    
    # 4. 獲取當前的節氣
    # getPrevJieQi(True) 代表獲取當下這個時間點「已經交過」的最近一個節氣
    jieqi = lunar.getPrevJieQi(True)
    jieqi_name = jieqi.getName()
    
    # 5. 打包成字典回傳
    result = {
        "輸入時間": dt_obj.strftime("%Y-%m-%d %H:%M:%S"),
        "年柱": year_ganzhi,
        "月柱": month_ganzhi,
        "日柱": day_ganzhi,
        "時柱": time_ganzhi,
        "當前節氣": jieqi_name
    }
    
    return result

# ==========================================
# 測試區塊：拿我們剛才的實戰盤來測試精準度
# 測試時間：2026年4月27日 21:51
# ==========================================
if __name__ == "__main__":
    # 建立一個測試時間
    test_time = datetime(2026, 4, 27, 21, 51, 0)
    
    print("啟動奇門時間引擎測試...\n")
    params = get_qimen_time_params(test_time)
    
    for key, value in params.items():
        print(f"{key}: {value}")
        
    print("\n✅ 導師核對點：日柱必須是『辛未』，時柱必須是『己亥』。如果吻合，代表地基建置成功！")