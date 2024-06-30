import os
from openai import OpenAI
import streamlit as st
import json
import pandas as pd
from awesome_table import AwesomeTable, Column
import time

os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),)

st.set_page_config(
   page_title="Shifteasy",
   page_icon="🥝",
   layout="wide",
   initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .header-text {
        color: #3D1386;
        text-align: center;
        margin-bottom:20px;
    }
    
      
    </style>
    """,
    unsafe_allow_html=True
)

# CSS 스타일을 포함한 HTML 코드
header_html = """
    <style>
    .header {
        font-size: 5em;
        text-align: center;
        border-bottom: 5px solid;
        background-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet);
        background-clip: text;
        -webkit-background-clip: text;
        color: transparent;
    }
    </style>
    <div class="header">Shifteasy</div>
"""

# st.markdown을 사용하여 HTML을 렌더링
st.markdown(header_html, unsafe_allow_html=True)
st.header('', divider='gray')

st.markdown('<h1 class="header-text">회사 정보</h1>', unsafe_allow_html=True)
company_name = st.text_input("회사 이름")
number_of_employees = st.number_input("직원 수", min_value=1, step=1)
work_shift_type = st.selectbox("근무 형태", ["근무형태를 선택하세요", "2교대", "3교대"])

if work_shift_type == "근무형태를 선택하세요":
    morning_shift = "" 
    night_shift = "" 
    required_staff_per_shift = {
        "shift1": morning_shift,
        "shift2": night_shift
    }
elif work_shift_type == "2교대":
    morning_shift = st.number_input("오전 근무 필수 인원수", min_value=1, step=1, key='morning_shift')
    night_shift = st.number_input("야간 근무 필수 인원수", min_value=1, step=1, key='night_shift')
    required_staff_per_shift = {
        "shift1": morning_shift,
        "shift2": night_shift
    }
else:  # 3교대
    morning_shift = st.number_input("오전 근무 필수 인원수", min_value=1, step=1, key='morning_shift')
    afternoon_shift = st.number_input("오후 근무 필수 인원수", min_value=1, step=1, key='afternoon_shift')
    night_shift = st.number_input("야간 근무 필수 인원수", min_value=1, step=1, key='night_shift')
    required_staff_per_shift = {
        "shift1": morning_shift,
        "shift2": afternoon_shift,
        "shift3": night_shift
    }

# 폼 제출 버튼
submit_button_company = st.button(label='회사 정보 제출')

company_data=[]
if submit_button_company:
    if company_name and required_staff_per_shift and number_of_employees and work_shift_type != "근무형태를 선택하세요":
        company_data.append({"company_name": company_name, "work_shift_type": work_shift_type, "number_of_employees":number_of_employees, "required_staff_per_shift":required_staff_per_shift})
        st.success(company_name + "의 정보가 저장되었습니다.")
        json_data = json.dumps(company_data, ensure_ascii=False)
    else:
        st.warning("회사 정보를 모두 입력해주세요.")
    # st.json(json_data)

# 직원 휴무 정보 입력 폼
st.markdown('<h1 class="header-text">직원 휴무 정보</h1>', unsafe_allow_html=True)
if "users" not in st.session_state:
    st.session_state["users"] = []

# Define the form
with st.form(key='user_form', clear_on_submit=True):
    # Text input for name
    name = st.text_input("이름")

    # Date input for preferred day off
    preferred_day_off = st.date_input("희망 휴무일")

    # Save button
    if st.form_submit_button('저장'):
        # Validate inputs if needed
        if name and preferred_day_off:
            # Save data to 'users' list
            preferred_day_off_str = preferred_day_off.strftime("%Y-%m-%d")
            st.session_state["users"].append({"name": name, "preferred_day_off": preferred_day_off_str})
            st.success(name + "의 휴무일이 저장되었습니다.")
            # Clear the form fields
            name = ""
            preferred_day_off = ""
        else:
            st.warning("이름과 희망 휴무일을 입력해주세요.")

json_user_data = json.dumps(st.session_state["users"], ensure_ascii=False, indent=4)
      
# 시간표 생성
st.markdown('<h1 class="header-text">스케줄 생성</h1>', unsafe_allow_html=True)
if 'selected_month' not in st.session_state:
    st.session_state.selected_month = 1

selected_month = st.selectbox("", list(range(1, 13)), format_func=lambda x: f"{x}월", index=st.session_state.selected_month-1)
st.session_state.selected_month = selected_month

submit_button_schedule = st.button(label=f'{selected_month}월 시간표 생성하기')

result=""
if submit_button_schedule:
    with st.spinner(f'{selected_month}월 스케쥴을 생성중입니다...🔥🔥🔥🔥🔥'):
        time.sleep(2)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": '한달 근무',
                },
                {
                    "role": "system",
                    "content": "입력 받은 키워드에 대한 150자 이내로 직원들을 힘나게 할 수 있는 문구를 만들어줘 ",
                }
            ],
            model="gpt-4o",
        )

    result = chat_completion.choices[0].message.content
    st.subheader(result +':sunglasses:')

if result:
    json_file_path = "result.json"

    # JSON 파일 읽기
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sample_data = data

    # 각 shift 값에 따른 이모지 매핑
    emoji_map = {
        "0": "",
        "1": "☀️️️",
        "2": "🌑",
        "3": "🔳"
    }

    # 최대 shift 길이 계산
    max_shift_length = max(len(user["shift"]) for user in sample_data)

    # AwesomeTable 구성
    columns = [
        Column(name='name', label='이름'),
        *[Column(name=f'shift_{i+1}', label=f'{i+1}') for i in range(max_shift_length)]
    ]


    # 데이터 프레임 생성
    data_dict = {
        f'shift_{i+1}': [emoji_map[user["shift"][i]] if i < len(user["shift"]) and user["shift"][i] in emoji_map else "" for user in sample_data]
        for i in range(max_shift_length)
    }
    data_dict['name'] = [user['name'] for user in sample_data]
    df = pd.DataFrame(data_dict)

    # AwesomeTable 생성
    awesome_table = AwesomeTable(df, columns=columns, show_order=False, show_search=False, show_search_order_in_sidebar=False)