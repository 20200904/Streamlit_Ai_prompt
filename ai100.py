import os
from openai import OpenAI
import streamlit as st
import json
import pandas as pd
from awesome_table import AwesomeTable, Column
import time

# Set API key for OpenAI
os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Page configuration
st.set_page_config(
    page_title="Shifteasy",
    page_icon="🥝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .header-text {
        color: #3D1386;
        text-align: center;
        margin-bottom:20px;
    }
    
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
    """,
    unsafe_allow_html=True
)

# Render header
header_html = """
<div class="header">Shifteasy</div>
"""
st.markdown(header_html, unsafe_allow_html=True)
st.header('', divider='gray')

# Company information input
st.markdown('<h1 class="header-text">회사 정보</h1>', unsafe_allow_html=True)
company_name = st.text_input("회사 이름")
number_of_employees = st.number_input("직원 수", min_value=1, step=1)
work_shift_type = st.selectbox("근무 형태", ["근무형태를 선택하세요", "2교대", "3교대"])

required_staff_per_shift = {}
if work_shift_type == "2교대":
    morning_shift = st.number_input("오전 근무 필수 인원수", min_value=1, step=1, key='morning_shift')
    night_shift = st.number_input("야간 근무 필수 인원수", min_value=1, step=1, key='night_shift')
    required_staff_per_shift = {
        "shift1": morning_shift,
        "shift2": night_shift
    }
elif work_shift_type == "3교대":
    morning_shift = st.number_input("오전 근무 필수 인원수", min_value=1, step=1, key='morning_shift')
    afternoon_shift = st.number_input("오후 근무 필수 인원수", min_value=1, step=1, key='afternoon_shift')
    night_shift = st.number_input("야간 근무 필수 인원수", min_value=1, step=1, key='night_shift')
    required_staff_per_shift = {
        "shift1": morning_shift,
        "shift2": afternoon_shift,
        "shift3": night_shift
    }

# Submit company information
submit_button_company = st.button(label='회사 정보 제출')
company_data = []
if submit_button_company:
    if company_name and required_staff_per_shift and number_of_employees and work_shift_type != "근무형태를 선택하세요":
        company_data.append({
            "company_name": company_name,
            "work_shift_type": work_shift_type,
            "number_of_employees": number_of_employees,
            "required_staff_per_shift": required_staff_per_shift
        })
        st.success(company_name + "의 정보가 저장되었습니다.")
    else:
        st.warning("회사 정보를 모두 입력해주세요.")

# Employee day off information input
st.markdown('<h1 class="header-text">직원 휴무 정보</h1>', unsafe_allow_html=True)
if "users" not in st.session_state:
    st.session_state["users"] = []

# Define the form for employee day off
with st.form(key='user_form', clear_on_submit=True):
    name = st.text_input("이름")
    preferred_day_off = st.date_input("희망 휴무일")
    if st.form_submit_button('저장'):
        if name and preferred_day_off:
            preferred_day_off_str = preferred_day_off.strftime("%Y-%m-%d")
            st.session_state["users"].append({"name": name, "preferred_day_off": preferred_day_off_str})
            st.success(name + "의 휴무일이 저장되었습니다.")
        else:
            st.warning("이름과 희망 휴무일을 입력해주세요.")

# Schedule generation
st.markdown('<h1 class="header-text">스케줄 생성</h1>', unsafe_allow_html=True)
if 'selected_month' not in st.session_state:
    st.session_state.selected_month = 1

selected_month = st.selectbox("", list(range(1, 13)), format_func=lambda x: f"{x}월", index=st.session_state.selected_month-1)
st.session_state.selected_month = selected_month

submit_button_schedule = st.button(label=f'{selected_month}월 시간표 생성하기')

result = ""
if submit_button_schedule:
    if not company_data or not st.session_state["users"]:
        st.warning("회사 정보와 직원 정보를 모두 입력해주세요.")
    else:
        with st.spinner(f'{selected_month}월 스케쥴을 생성중입니다...🔥🔥🔥🔥🔥'):
            time.sleep(2)
            
            # Create prompt content based on user inputs
            company_info = company_data[0]
            employees_info = st.session_state["users"]
            prompt_content = f'''
            회사정보 :
            {{
                "company_name": "{company_info['company_name']}",
                "work_shift_type": "{company_info['work_shift_type']}",
                "number_of_employees": {company_info['number_of_employees']},
                "required_staff_per_shift": {json.dumps(company_info['required_staff_per_shift'])},
                "month": {selected_month}
            }}
            직원 정보 :
            {json.dumps(employees_info, ensure_ascii=False)}
            '''
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt_content
                    },
                    {
                        "role": "system",
                        "content": '''
                        Create a balanced work schedule for a company with the following data:
                        - "number_of_employees": 10
                        - "required_staff_per_shift":
                            - "shift1": 3 (morning shift)
                            - "shift2": 2 (afternoon shift)
                            - "shift3": 2 (evening shift)
                            - "shift0": 3 (day off)
                            - "month": 6 (June, with 30 days)
                        Ensure that:
                        - Each day, exactly 3 employees are assigned to shift1 (morning), 2 to shift2 (afternoon), 2 to shift3 (evening), and 3 have a day off (shift0).
                        - The schedule is balanced so that the workload is evenly distributed among all employees.
                        Output the schedule in JSON format as follows:
                        [
                            {"name": "<employee_name>", "shift": [<shifts for each day of the month>]},
                            ...
                        ]
                        Example output for a company with 10 employees for the month of June (30 days):
                        [
                            {"name": "Employee1", "shift": ["1", "0", "2", "1", "3", "0", "1", "2", "3", "0", "1", "2", "1", "0", "3", "2", "1", "0", "1", "3", "0", "2", "1", "3", "0", "1", "2", "1", "0", "3"]},
                            ...
                        ]
                        The schedule should ensure that each shift (morning, afternoon, evening) and day off is properly distributed among all employees, meeting the staffing requirements each day. When generating the "shift" array for each employee, 1 represents shift1 (morning), 2 represents shift2 (afternoon), 3 represents shift3 (evening), and 0 represents shift0 (day off).
                        '''
                    }
                ],
                model="gpt-4",
            )

        result = chat_completion.choices[0].message.content
        st.subheader(result + ':sunglasses:')

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
            data_dict['name'] = [user["name"] for user in sample_data]
            df = pd.DataFrame(data_dict)

            # AwesomeTable 렌더링
            AwesomeTable(df, columns=columns, show_search=True, show_sort=True, key="awesome_table")
