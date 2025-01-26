import streamlit as st
from openai import OpenAI
import json

document ='''荷花姐姐的珍珠不見了!
青蛙說：「我幫你找。」
ㄆㄨㄊㄨㄥ！ㄆㄨㄊㄨㄥ！
青蛙跳下水，
東找找,西找找，
就是找不到。

小魚說:「我幫你找。」
ㄆㄚㄌㄚ！ㄆㄚㄌㄚ！
小魚到處找，
東找找,西找找，
還是找不到。

天黑了，
月亮出來散步。
荷花姐姐 說：
「月亮！月亮！
請你幫個忙···· 」

月亮笑著說：
「不用找，不用找，
明天清晨
珍珠就回來啦!」'''

out_format ='''{"選擇題":[
    {
        "題目":"誰最先提出要幫荷花姐姐找珍珠？",
        "選項":[
            "A. 小魚",
            "B. 青蛙",
            "C. 月亮",
            "D. 荷花姐姐"
        ],
        "答案":"B"
    },
],
"是非題":[
    {
        "題目":"青蛙和小魚都幫荷花姐姐找珍珠，卻找不到。 (對/錯)",
        "答案":"對"
    },
]}'''

client = OpenAI()

# Streamlit App Layout
st.set_page_config(layout="wide", page_title="考題生成器", page_icon="📝")  # 設置寬屏模式

if 'state' not in st.session_state:
    st.session_state.state = 0
    
if 'data' not in st.session_state:
    st.session_state.data = {}
    
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}

# Streamlit App Layout
st.title("📝 考題生成器")
st.write("根據文章自動生成選擇題和是非題，並進行答題測試！")
st.write("")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ 請輸入以下選項", anchor=None)
    article = st.text_area("請輸入文章：", value=document, height=200)
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_choices = st.number_input("生成幾題選擇題：", min_value=1, max_value=10, value=3, step=1)
    with col2:
        num_true_false = st.number_input("生成幾題是非題：", min_value=1, max_value=10, value=3, step=1)
    
    temperature = st.slider("設定temperature控制生成文本的隨機性：", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
    generate_button = st.button("生成考題")
    
# Main Content Section
if generate_button:
    if not article.strip():
        st.warning("請輸入文章後再生成考題！")
    else:
        # OpenAI GPT Request
        prompt = (
            f"請根據以下的文章，出{num_choices}題有4個備選答案的選擇題，"
            f"以及{num_true_false}題是非題。文章如下：{article}"
        )

        with st.spinner("生成考題中，請稍候..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # 選擇使用的模型
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "你是一個小學老師, 想要出考題考學生，"+
                                "希望輸出的格式如下："+out_format
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                )

                st.session_state.data = json.loads(response.choices[0].message.content)

                st.session_state.user_answers = {}
                st.session_state.state = 1

            except Exception as e:
                st.error(f"生成考題時出現錯誤：{e}")
                
if st.session_state.state == 1:                
    st.subheader("🔢生成的選擇題")

    for i, q in enumerate(st.session_state.data['選擇題']):
        st.write(f"**{i + 1}. {q['題目']}**")
        st.session_state.user_answers[f"choice_{i}"] = st.radio(
            label="", label_visibility="collapsed", options=[opt for opt in q['選項']], key=f"choice_{i}"
        )

    st.write("")
    
    st.subheader("🎯生成的是非題")
    
    for i, q in enumerate(st.session_state.data['是非題']):
        st.write(f"**{i + 1}. {q['題目']}**")
        st.session_state.user_answers[f"true_false_{i}"] = st.radio(
            label="", label_visibility="collapsed", options=["對", "錯"], key=f"true_false_{i}"
        )

    if st.button("提交所有答案"):
        st.session_state.state = 2
        st.rerun()
        
if st.session_state.state == 2:      
    total_score = 0
    correct_score = 0

    st.subheader("🔢生成的選擇題")

    for i, q in enumerate(st.session_state.data['選擇題']):
        st.write(f"**{i + 1}. {q['題目']}**")
        st.session_state.user_answers[f"choice_{i}"] = st.radio(
            label="", label_visibility="collapsed", options=[opt for opt in q['選項']], key=f"choice_{i}"
        )
        
        if st.session_state.user_answers[f"choice_{i}"][0] == q['答案']:
            st.markdown("✅ 正確： 答案是 " + q['答案'] +"。")
            correct_score += 1
        else:
            st.markdown("❌ 錯誤： 答案是 " + q['答案'] +"。")
        total_score += 1
     
    st.write("")
    
    st.subheader("🎯生成的是非題")

    for i, q in enumerate(st.session_state.data['是非題']):
        st.write(f"**{i + 1}. {q['題目']}**")
        st.session_state.user_answers[f"true_false_{i}"] = st.radio(
            label="", label_visibility="collapsed", options=["對", "錯"], key=f"true_false_{i}"
        )
        
        if st.session_state.user_answers[f"true_false_{i}"] == q['答案']:
            st.markdown("✅ 正確： 答案是 " + q['答案'] +"。")
            correct_score += 1
        else:
            st.markdown("❌ 錯誤： 答案是 " + q['答案'] +"。")
        total_score += 1

    # Display Total Score
    st.write(f"### 您的總得分：{correct_score}/{total_score}")
    
    if st.button("重新答題"):
        st.session_state.state = 1
        st.rerun()