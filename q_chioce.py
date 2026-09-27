import streamlit as st
import pandas as pd
import requests
import base64

from io import StringIO


# =========================================================
# Page Config
# =========================================================

st.set_page_config(
    page_title="AIDDES 問卷資料查詢",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# GitHub 設定
# =========================================================

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]

BRANCH = "main"

CCMQ_FILE = "ccmq_data.csv"
OSDI_FILE = "osdi_data.csv"

GITHUB_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
<style>

.stApp {
    background-color: #F3EEE7;
}

.block-container {
    max-width: 1250px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}


/* ===================================================== */
/* 標題 */
/* ===================================================== */

h1,
h2,
h3 {
    color: #5B4D43 !important;
}

p,
label {
    color: #65584F;
}


/* ===================================================== */
/* Input */
/* ===================================================== */

.stTextInput input {
    background-color: #FFFDFC !important;
    border: 1px solid #D8C9BB !important;
    border-radius: 12px !important;
    min-height: 48px;
    color: #4D423B !important;
}

.stTextInput input:focus {
    border-color: #A68C78 !important;
    box-shadow: 0 0 0 1px #A68C78 !important;
}


/* ===================================================== */
/* Selectbox */
/* ===================================================== */

div[data-baseweb="select"] > div {
    background-color: #FFFDFC !important;
    border: 1px solid #D8C9BB !important;
    border-radius: 12px !important;
    min-height: 48px;
}


/* ===================================================== */
/* Button */
/* ===================================================== */

.stButton > button {
    width: 100%;
    background-color: #A68C78;
    color: white;
    border: none;
    border-radius: 12px;
    min-height: 48px;
    font-size: 16px;
    font-weight: 600;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background-color: #8D7361;
    color: white;
    border: none;
}

.stButton > button:focus {
    color: white;
}


/* ===================================================== */
/* 首頁 */
/* ===================================================== */

.home-card {
    max-width: 720px;
    margin: 28px auto 25px auto;
    background-color: #FFFDFC;
    border: 1px solid #DED0C4;
    border-radius: 22px;
    padding: 34px 36px;
    text-align: center;
}

.home-card-title {
    font-size: 22px;
    font-weight: 700;
    color: #655448;
    margin-bottom: 12px;
}

.home-card-text {
    font-size: 16px;
    color: #88766A;
    line-height: 1.8;
}


/* ===================================================== */
/* 提示框 */
/* ===================================================== */

.hint-box {
    background-color: #ECE2D8;
    border-radius: 14px;
    padding: 15px 20px;
    color: #65564B;
    margin: 12px 0 22px 0;
    line-height: 1.7;
}


/* ===================================================== */
/* 個人資料 */
/* ===================================================== */

.info-box {
    background-color: #E9DED3;
    border-radius: 18px;
    padding: 20px 24px;
    margin-bottom: 24px;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 22px;
}

.info-label {
    font-size: 13px;
    color: #897568;
    margin-bottom: 5px;
}

.info-value {
    font-size: 18px;
    font-weight: 700;
    color: #51443C;
}


/* ===================================================== */
/* 下拉選單區塊 */
/* ===================================================== */

.select-card {
    background-color: #FFFDFC;
    border: 1px solid #DFD3C8;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 15px;
}

.select-title {
    font-size: 20px;
    font-weight: 700;
    color: #655347;
    margin-bottom: 5px;
}

.select-subtitle {
    font-size: 14px;
    color: #8A786B;
    margin-bottom: 10px;
}


/* ===================================================== */
/* 問卷卡片 */
/* ===================================================== */

.question-card {
    background-color: #FFFDFC;
    border: 1px solid #DFD3C8;
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 15px;
    box-shadow: 0px 3px 10px rgba(86, 67, 52, 0.04);
}

.question-card-title {
    font-size: 21px;
    font-weight: 700;
    color: #655347;
    padding-bottom: 14px;
    margin-bottom: 4px;
    border-bottom: 2px solid #E9DFD7;
}

.question-row {
    padding: 12px 2px;
    border-bottom: 1px solid #EEE7E1;
}

.question-row:last-child {
    border-bottom: none;
}

.question-name {
    font-size: 14px;
    color: #8A786B;
    margin-bottom: 4px;
}

.question-value {
    font-size: 16px;
    font-weight: 600;
    color: #4C4038;
}


/* ===================================================== */
/* 問卷時間 */
/* ===================================================== */

.time-box {
    background-color: #ECE2D8;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 12px;
    color: #66564B;
    font-size: 14px;
}


/* ===================================================== */
/* 手機版 */
/* ===================================================== */

@media (max-width: 768px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .info-grid {
        grid-template-columns: 1fr;
        gap: 14px;
    }

    .home-card {
        padding: 25px 20px;
    }
}

footer {
    visibility: hidden;
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# Session State
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "search_name" not in st.session_state:
    st.session_state.search_name = ""

if "search_phone" not in st.session_state:
    st.session_state.search_phone = ""

if "ccmq_records" not in st.session_state:
    st.session_state.ccmq_records = []

if "osdi_records" not in st.session_state:
    st.session_state.osdi_records = []

if "selected_ccmq" not in st.session_state:
    st.session_state.selected_ccmq = None

if "selected_osdi" not in st.session_state:
    st.session_state.selected_osdi = None

if "selected_ccmq_time" not in st.session_state:
    st.session_state.selected_ccmq_time = ""

if "selected_osdi_time" not in st.session_state:
    st.session_state.selected_osdi_time = ""

if "has_searched" not in st.session_state:
    st.session_state.has_searched = False


# =========================================================
# GitHub 讀 CSV
# =========================================================

@st.cache_data(ttl=60)
def load_csv_from_github(file_path):

    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_REPO}/contents/{file_path}"
    )

    try:

        response = requests.get(
            url,
            headers=GITHUB_HEADERS,
            params={"ref": BRANCH},
            timeout=15
        )

    except requests.RequestException:
        return pd.DataFrame()

    if response.status_code != 200:
        return pd.DataFrame()

    try:

        data = response.json()

        content = base64.b64decode(
            data["content"]
        ).decode("utf-8-sig")

        df = pd.read_csv(
            StringIO(content),
            dtype=str
        )

        return df.fillna("")

    except Exception:
        return pd.DataFrame()


# =========================================================
# 找欄位
# =========================================================

def find_column(df, candidates):

    for column in candidates:

        if column in df.columns:
            return column

    return None


def get_name_column(df):

    return find_column(
        df,
        [
            "姓名",
            "name",
            "Name",
            "受試者姓名"
        ]
    )


def get_phone_column(df):

    return find_column(
        df,
        [
            "電話",
            "phone",
            "Phone",
            "手機",
            "手機號碼",
            "聯絡電話"
        ]
    )


# =========================================================
# 電話清理
# =========================================================

def clean_phone(value):

    value = str(value).strip()

    for symbol in [
        "-",
        " ",
        "(",
        ")"
    ]:
        value = value.replace(symbol, "")

    if value.endswith(".0"):
        value = value[:-2]

    if (
        len(value) == 9
        and value.startswith("9")
    ):
        value = "0" + value

    return value


# =========================================================
# 取得時間
# =========================================================

def get_time_value(row):

    candidates = [
        "填寫時間",
        "填寫日期",
        "timestamp",
        "Timestamp",
        "時間",
        "日期",
        "datetime",
        "created_at",
        "提交時間"
    ]

    for column in candidates:

        if column in row.index:

            value = str(
                row[column]
            ).strip()

            if (
                value
                and value.lower() != "nan"
            ):
                return value

    return "未記錄時間"


# =========================================================
# HTML Escape
# =========================================================

def escape_html(value):

    value = str(value)

    return (
        value
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


# =========================================================
# 回首頁
# =========================================================

def reset_and_home():

    st.session_state.page = "home"

    st.session_state.search_name = ""
    st.session_state.search_phone = ""

    st.session_state.ccmq_records = []
    st.session_state.osdi_records = []

    st.session_state.selected_ccmq = None
    st.session_state.selected_osdi = None

    st.session_state.selected_ccmq_time = ""
    st.session_state.selected_osdi_time = ""

    st.session_state.has_searched = False

    st.rerun()


# =========================================================
# 首頁
# =========================================================

def home():

    st.markdown(
        """
<div style="text-align:center;padding-top:45px;padding-bottom:18px;">
<div style="font-size:38px;font-weight:700;color:#5C4E44;margin-bottom:10px;">
AIDDES 問卷資料查詢
</div>
<div style="font-size:17px;color:#857467;">
查詢 CCMQ 與 OSDI 問卷紀錄
</div>
</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="home-card">
<div class="home-card-title">
問卷資料查詢
</div>
<div class="home-card-text">
輸入受試者姓名與電話後，可查詢過去填寫的 CCMQ 與 OSDI 紀錄。
<br>
CCMQ 與 OSDI 可分別選擇不同的填寫紀錄。
</div>
</div>
""",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(
        [1.5, 2, 1.5]
    )

    with col2:

        if st.button(
            "開始查詢",
            use_container_width=True
        ):

            st.session_state.page = "search"
            st.rerun()


# =========================================================
# 查詢頁
# =========================================================

def search_page():

    # =====================================================
    # 標題
    # =====================================================

    st.markdown(
        """
<div style="text-align:center;margin-bottom:25px;">
<div style="font-size:32px;font-weight:700;color:#5C4E44;margin-bottom:8px;">
問卷資料查詢
</div>
<div style="font-size:16px;color:#857467;">
請輸入姓名與電話
</div>
</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="hint-box">
系統會分別搜尋該受試者所有 CCMQ 與 OSDI 紀錄，
您可以在兩個下拉選單中分別選擇想查看的資料。
</div>
""",
        unsafe_allow_html=True
    )


    # =====================================================
    # 讀取資料
    # =====================================================

    with st.spinner(
        "正在讀取問卷資料..."
    ):

        ccmq_df = (
            load_csv_from_github(
                CCMQ_FILE
            )
        )

        osdi_df = (
            load_csv_from_github(
                OSDI_FILE
            )
        )


    if ccmq_df.empty:

        st.error(
            f"無法讀取 {CCMQ_FILE}"
        )

        return


    if osdi_df.empty:

        st.error(
            f"無法讀取 {OSDI_FILE}"
        )

        return


    # =====================================================
    # 找姓名電話欄位
    # =====================================================

    ccmq_name_col = (
        get_name_column(ccmq_df)
    )

    ccmq_phone_col = (
        get_phone_column(ccmq_df)
    )

    osdi_name_col = (
        get_name_column(osdi_df)
    )

    osdi_phone_col = (
        get_phone_column(osdi_df)
    )


    if not all(
        [
            ccmq_name_col,
            ccmq_phone_col,
            osdi_name_col,
            osdi_phone_col
        ]
    ):

        st.error(
            "找不到姓名或電話欄位。"
        )

        st.write(
            "CCMQ 欄位：",
            list(ccmq_df.columns)
        )

        st.write(
            "OSDI 欄位：",
            list(osdi_df.columns)
        )

        return


    # =====================================================
    # 搜尋欄位
    # =====================================================

    col1, col2 = st.columns(
        2,
        gap="large"
    )

    with col1:

        name = st.text_input(
            "姓名",
            value=(
                st.session_state
                .search_name
            ),
            placeholder="請輸入姓名"
        )


    with col2:

        phone = st.text_input(
            "電話",
            value=(
                st.session_state
                .search_phone
            ),
            placeholder="例如：0912345678"
        )


    # =====================================================
    # 搜尋
    # =====================================================

    if st.button(
        "搜尋資料",
        use_container_width=True
    ):

        st.session_state.has_searched = True

        st.session_state.ccmq_records = []
        st.session_state.osdi_records = []


        if (
            not name.strip()
            or not phone.strip()
        ):

            st.warning(
                "請完整輸入姓名與電話。"
            )


        else:

            input_name = name.strip()

            input_phone = (
                clean_phone(phone)
            )


            st.session_state.search_name = (
                input_name
            )

            st.session_state.search_phone = (
                input_phone
            )


            # =================================================
            # CCMQ 搜尋
            # =================================================

            ccmq_phone_clean = (
                ccmq_df[
                    ccmq_phone_col
                ]
                .astype(str)
                .apply(clean_phone)
            )


            ccmq_person = ccmq_df[
                (
                    ccmq_df[
                        ccmq_name_col
                    ]
                    .astype(str)
                    .str.strip()
                    == input_name
                )
                &
                (
                    ccmq_phone_clean
                    == input_phone
                )
            ].copy()


            # =================================================
            # OSDI 搜尋
            # =================================================

            osdi_phone_clean = (
                osdi_df[
                    osdi_phone_col
                ]
                .astype(str)
                .apply(clean_phone)
            )


            osdi_person = osdi_df[
                (
                    osdi_df[
                        osdi_name_col
                    ]
                    .astype(str)
                    .str.strip()
                    == input_name
                )
                &
                (
                    osdi_phone_clean
                    == input_phone
                )
            ].copy()


            # =================================================
            # CCMQ 全部紀錄
            # =================================================

            ccmq_records = []

            for _, row in (
                ccmq_person.iterrows()
            ):

                ccmq_records.append(
                    {
                        "time":
                            get_time_value(
                                row
                            ),

                        "data":
                            row.to_dict()
                    }
                )


            # =================================================
            # OSDI 全部紀錄
            # =================================================

            osdi_records = []

            for _, row in (
                osdi_person.iterrows()
            ):

                osdi_records.append(
                    {
                        "time":
                            get_time_value(
                                row
                            ),

                        "data":
                            row.to_dict()
                    }
                )


            st.session_state.ccmq_records = (
                ccmq_records
            )

            st.session_state.osdi_records = (
                osdi_records
            )


    # =====================================================
    # 搜尋結果
    # =====================================================

    ccmq_records = (
        st.session_state
        .ccmq_records
    )

    osdi_records = (
        st.session_state
        .osdi_records
    )


    if (
        ccmq_records
        or osdi_records
    ):

        st.divider()


        # =================================================
        # 個人資訊
        # =================================================

        name_html = escape_html(
            st.session_state.search_name
        )

        phone_html = escape_html(
            st.session_state.search_phone
        )


        st.markdown(
            f"""
<div class="info-box">
<div class="info-grid">

<div>
<div class="info-label">
姓名
</div>
<div class="info-value">
{name_html}
</div>
</div>

<div>
<div class="info-label">
電話
</div>
<div class="info-value">
{phone_html}
</div>
</div>

<div>
<div class="info-label">
搜尋結果
</div>
<div class="info-value">
CCMQ {len(ccmq_records)} 筆 ｜ OSDI {len(osdi_records)} 筆
</div>
</div>

</div>
</div>
""",
            unsafe_allow_html=True
        )


        # =================================================
        # 兩個下拉選單
        # =================================================

        left, right = st.columns(
            2,
            gap="large"
        )


        # =================================================
        # CCMQ
        # =================================================

        with left:

            st.markdown(
                """
<div class="select-card">
<div class="select-title">
CCMQ 中醫體質問卷
</div>
<div class="select-subtitle">
選擇想查看的 CCMQ 紀錄
</div>
</div>
""",
                unsafe_allow_html=True
            )


            if ccmq_records:

                ccmq_options = list(
                    range(
                        len(
                            ccmq_records
                        )
                    )
                )


                def ccmq_label(i):

                    time = (
                        ccmq_records[i]
                        .get(
                            "time",
                            "未記錄時間"
                        )
                    )

                    return (
                        f"第 {i + 1} 筆 ｜ "
                        f"{time}"
                    )


                selected_ccmq_index = (
                    st.selectbox(
                        "選擇 CCMQ 紀錄",
                        options=ccmq_options,
                        format_func=ccmq_label,
                        key="ccmq_select"
                    )
                )


            else:

                selected_ccmq_index = None

                st.warning(
                    "找不到 CCMQ 紀錄"
                )


        # =================================================
        # OSDI
        # =================================================

        with right:

            st.markdown(
                """
<div class="select-card">
<div class="select-title">
OSDI 乾眼症問卷
</div>
<div class="select-subtitle">
選擇想查看的 OSDI 紀錄
</div>
</div>
""",
                unsafe_allow_html=True
            )


            if osdi_records:

                osdi_options = list(
                    range(
                        len(
                            osdi_records
                        )
                    )
                )


                def osdi_label(i):

                    time = (
                        osdi_records[i]
                        .get(
                            "time",
                            "未記錄時間"
                        )
                    )

                    return (
                        f"第 {i + 1} 筆 ｜ "
                        f"{time}"
                    )


                selected_osdi_index = (
                    st.selectbox(
                        "選擇 OSDI 紀錄",
                        options=osdi_options,
                        format_func=osdi_label,
                        key="osdi_select"
                    )
                )


            else:

                selected_osdi_index = None

                st.warning(
                    "找不到 OSDI 紀錄"
                )


        # =================================================
        # 確認提示
        # =================================================

        st.markdown(
            """
<div class="hint-box">
請分別選擇一筆 CCMQ 與一筆 OSDI 紀錄。
選擇完成後按下「確認查看」。
</div>
""",
            unsafe_allow_html=True
        )


        # =================================================
        # 確認
        # =================================================

        if (
            selected_ccmq_index is not None
            and
            selected_osdi_index is not None
        ):

            if st.button(
                "確認查看",
                type="primary",
                use_container_width=True
            ):

                # CCMQ
                st.session_state.selected_ccmq = (
                    ccmq_records[
                        selected_ccmq_index
                    ]["data"]
                )

                st.session_state.selected_ccmq_time = (
                    ccmq_records[
                        selected_ccmq_index
                    ]["time"]
                )


                # OSDI
                st.session_state.selected_osdi = (
                    osdi_records[
                        selected_osdi_index
                    ]["data"]
                )

                st.session_state.selected_osdi_time = (
                    osdi_records[
                        selected_osdi_index
                    ]["time"]
                )


                st.session_state.page = (
                    "result"
                )

                st.rerun()


    # =====================================================
    # 完全找不到
    # =====================================================

    elif (
        st.session_state.has_searched
        and
        st.session_state.search_name
        and
        st.session_state.search_phone
    ):

        st.warning(
            "找不到此姓名與電話的問卷紀錄。"
        )


    # =====================================================
    # 返回首頁
    # =====================================================

    st.write("")
    st.write("")


    if st.button(
        "返回首頁",
        use_container_width=True,
        key="search_back"
    ):

        reset_and_home()


# =========================================================
# 顯示單份問卷
# =========================================================

def display_questionnaire(
    title,
    data,
    skip_columns=None
):

    if skip_columns is None:
        skip_columns = []


    # 不用縮排 multiline HTML
    # 避免被 Streamlit 當成 code block

    html = (
        '<div class="question-card">'
        f'<div class="question-card-title">'
        f'{escape_html(title)}'
        '</div>'
    )


    for key, value in data.items():

        if key in skip_columns:
            continue


        value = str(value).strip()


        if (
            value == ""
            or value.lower() == "nan"
        ):
            continue


        safe_key = (
            escape_html(key)
        )

        safe_value = (
            escape_html(value)
        )


        html += (
            '<div class="question-row">'
            f'<div class="question-name">'
            f'{safe_key}'
            '</div>'
            f'<div class="question-value">'
            f'{safe_value}'
            '</div>'
            '</div>'
        )


    html += '</div>'


    st.markdown(
        html,
        unsafe_allow_html=True
    )


# =========================================================
# 結果頁
# =========================================================

def result_page():

    ccmq_data = (
        st.session_state
        .selected_ccmq
    )

    osdi_data = (
        st.session_state
        .selected_osdi
    )


    if (
        ccmq_data is None
        or osdi_data is None
    ):

        st.session_state.page = "home"

        st.rerun()

        return


    # =====================================================
    # 標題
    # =====================================================

    st.markdown(
        """
<div style="text-align:center;margin-bottom:24px;">
<div style="font-size:34px;font-weight:700;color:#5C4E44;margin-bottom:7px;">
問卷資料
</div>
<div style="font-size:16px;color:#857467;">
CCMQ 與 OSDI 問卷結果
</div>
</div>
""",
        unsafe_allow_html=True
    )


    # =====================================================
    # 個人資訊
    # =====================================================

    name = (
        ccmq_data.get("姓名")
        or
        ccmq_data.get("name")
        or
        ccmq_data.get("Name")
        or
        osdi_data.get("姓名")
        or
        osdi_data.get("name")
        or
        ""
    )


    phone = (
        ccmq_data.get("電話")
        or
        ccmq_data.get("phone")
        or
        ccmq_data.get("Phone")
        or
        ccmq_data.get("手機")
        or
        osdi_data.get("電話")
        or
        osdi_data.get("phone")
        or
        ""
    )


    st.markdown(
        f"""
<div class="info-box">
<div class="info-grid">

<div>
<div class="info-label">
姓名
</div>
<div class="info-value">
{escape_html(name)}
</div>
</div>

<div>
<div class="info-label">
電話
</div>
<div class="info-value">
{escape_html(phone)}
</div>
</div>

<div>
<div class="info-label">
選取資料
</div>
<div class="info-value">
CCMQ + OSDI
</div>
</div>

</div>
</div>
""",
        unsafe_allow_html=True
    )


    # =====================================================
    # 不重複展示
    # =====================================================

    skip_columns = [
        "姓名",
        "name",
        "Name",
        "受試者姓名",

        "電話",
        "phone",
        "Phone",
        "手機",
        "手機號碼",
        "聯絡電話",

        "record_id",
        "Record_ID",
        "recordId",
        "紀錄編號",
        "紀錄ID"
    ]


    # =====================================================
    # 左 CCMQ / 右 OSDI
    # =====================================================

    left, right = st.columns(
        2,
        gap="large"
    )


    # =====================================================
    # CCMQ
    # =====================================================

    with left:

        st.markdown(
            (
                '<div class="time-box">'
                'CCMQ 填寫時間：'
                '<strong>'
                + escape_html(
                    st.session_state
                    .selected_ccmq_time
                )
                + '</strong>'
                '</div>'
            ),
            unsafe_allow_html=True
        )


        display_questionnaire(
            "CCMQ 中醫體質問卷",
            ccmq_data,
            skip_columns
        )


    # =====================================================
    # OSDI
    # =====================================================

    with right:

        st.markdown(
            (
                '<div class="time-box">'
                'OSDI 填寫時間：'
                '<strong>'
                + escape_html(
                    st.session_state
                    .selected_osdi_time
                )
                + '</strong>'
                '</div>'
            ),
            unsafe_allow_html=True
        )


        display_questionnaire(
            "OSDI 乾眼症問卷",
            osdi_data,
            skip_columns
        )


    # =====================================================
    # 返回首頁
    # =====================================================

    st.write("")
    st.write("")


    col1, col2, col3 = st.columns(
        [1.3, 2, 1.3]
    )


    with col2:

        if st.button(
            "返回首頁",
            use_container_width=True,
            key="result_back"
        ):

            reset_and_home()


# =========================================================
# Router
# =========================================================

if st.session_state.page == "home":

    home()


elif st.session_state.page == "search":

    search_page()


elif st.session_state.page == "result":

    result_page()
