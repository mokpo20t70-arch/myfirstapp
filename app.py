import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from collections import Counter
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# 페이지 설정
st.set_page_config(
    page_title="수업 이해도 체크",
    page_icon="📚",
    layout="wide"
)

# 세션 상태 초기화
if 'responses' not in st.session_state:
    st.session_state.responses = []
if 'learning_goals' not in st.session_state:
    st.session_state.learning_goals = [""] * 5
if 'current_date' not in st.session_state:
    st.session_state.current_date = datetime.now().strftime("%Y-%m-%d")

# CSS 스타일
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px;
        border-radius: 10px;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    .goal-box {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stat-box {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 탭 생성
tab1, tab2, tab3 = st.tabs(["👨‍🏫 교사 설정", "📝 학생 응답", "📊 결과 확인"])

# 탭1: 교사 설정
with tab1:
    st.header("🎯 오늘의 학습 목표 설정")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("💡 수업에서 달성해야 할 학습 목표 5가지를 입력해주세요")
    with col2:
        if st.button("🔄 목표 초기화"):
            st.session_state.learning_goals = [""] * 5
            st.rerun()
    
    # 학습 목표 입력
    for i in range(5):
        st.session_state.learning_goals[i] = st.text_input(
            f"학습 목표 {i+1}",
            value=st.session_state.learning_goals[i],
            placeholder=f"예: 시의 화자와 정서를 파악할 수 있다",
            key=f"goal_{i}"
        )
    
    # 저장 버튼
    if st.button("💾 학습 목표 저장", type="primary"):
        if all(st.session_state.learning_goals):
            st.success("✅ 학습 목표가 저장되었습니다!")
            # 파일로 저장
            goals_data = {
                'date': st.session_state.current_date,
                'goals': st.session_state.learning_goals
            }
            with open('learning_goals.json', 'w', encoding='utf-8') as f:
                json.dump(goals_data, f, ensure_ascii=False, indent=2)
        else:
            st.error("⚠️ 모든 학습 목표를 입력해주세요!")

# 탭2: 학생 응답
with tab2:
    st.header("📚 오늘 수업 이해도 체크")
    
    # 학생 정보
    col1, col2 = st.columns(2)
    with col1:
        student_num = st.number_input("📍 번호", min_value=1, max_value=40, step=1)
    with col2:
        class_name = st.selectbox("🏫 반", ["1반", "2반", "3반", "4반", "5반", "6반"])
    
    # 학습 목표 체크리스트
    st.markdown("### ✅ 학습 목표 달성 체크")
    st.markdown("*각 목표를 달성했다면 체크해주세요*")
    
    goal_checks = []
    for i, goal in enumerate(st.session_state.learning_goals):
        if goal:
            checked = st.checkbox(f"**{goal}**", key=f"check_{i}")
            goal_checks.append(checked)
    
    # 전체 이해도
    st.markdown("### 📊 전체 수업 이해도")
    understanding_level = st.slider(
        "오늘 수업을 얼마나 이해했나요?",
        min_value=1,
        max_value=5,
        value=3,
        format="%d점",
        help="1점: 매우 어려움, 5점: 완벽히 이해"
    )
    
    # 이해도 이모지 표시
    emojis = {1: "😵", 2: "😕", 3: "😐", 4: "🙂", 5: "😄"}
    st.markdown(f"<h2 style='text-align: center;'>{emojis[understanding_level]}</h2>", unsafe_allow_html=True)
    
    # 피드백
    st.markdown("### 💬 피드백 (선택사항)")
    col1, col2 = st.columns(2)
    with col1:
        difficult_part = st.text_area(
            "어려웠던 부분",
            placeholder="예: 시어의 함축적 의미 파악이 어려웠어요",
            height=100
        )
    with col2:
        help_needed = st.selectbox(
            "도움이 필요한 부분",
            ["선택 안 함", "개념 이해", "문제 풀이", "응용 연습", "심화 학습", "기타"]
        )
    
    # 제출 버튼
    if st.button("📤 제출하기", type="primary"):
        if any(goal_checks) or understanding_level:
            # 응답 저장
            response = {
                'timestamp': datetime.now().isoformat(),
                'date': st.session_state.current_date,
                'class': class_name,
                'student_num': student_num,
                'goal_checks': goal_checks,
                'understanding_level': understanding_level,
                'difficult_part': difficult_part,
                'help_needed': help_needed
            }
            st.session_state.responses.append(response)
            
            # 파일로 저장
            filename = f"responses_{st.session_state.current_date}.json"
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            else:
                existing_data = []
            
            existing_data.append(response)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            st.balloons()
            st.success("✅ 제출 완료! 수고했어요 👏")
        else:
            st.error("⚠️ 최소한 하나 이상의 항목을 체크해주세요!")

# 탭3: 결과 확인
with tab3:
    st.header("📊 실시간 결과 분석")
    
    # 데이터 로드
    filename = f"responses_{st.session_state.current_date}.json"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            responses = json.load(f)
    else:
        responses = st.session_state.responses
    
    if responses:
        # 기본 통계
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
            st.metric("📝 응답 학생 수", len(responses))
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            avg_understanding = sum(r['understanding_level'] for r in responses) / len(responses)
            st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
            st.metric("⭐ 평균 이해도", f"{avg_understanding:.1f} / 5.0")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            total_goals_achieved = sum(sum(r['goal_checks']) for r in responses)
            total_possible = len(responses) * len(st.session_state.learning_goals)
            if total_possible > 0:
                achievement_rate = (total_goals_achieved / total_possible) * 100
                st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
                st.metric("🎯 전체 목표 달성률", f"{achievement_rate:.1f}%")
                st.markdown("</div>", unsafe_allow_html=True)
        
        # 학습 목표별 달성률 막대그래프
        st.markdown("### 📈 학습 목표별 달성률")
        goal_achievement = []
        for i, goal in enumerate(st.session_state.learning_goals):
            if goal:
                achieved = sum(r['goal_checks'][i] if i < len(r['goal_checks']) else False for r in responses)
                rate = (achieved / len(responses)) * 100
                goal_achievement.append({
                    '학습 목표': f"목표 {i+1}",
                    '목표 내용': goal[:30] + "..." if len(goal) > 30 else goal,
                    '달성률': rate
                })
        
        if goal_achievement:
            df_goals = pd.DataFrame(goal_achievement)
            fig = px.bar(
                df_goals, 
                x='달성률', 
                y='목표 내용',
                orientation='h',
                color='달성률',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100],
                title="학습 목표별 달성률 (%)"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # 이해도 분포
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 이해도 분포")
            understanding_dist = Counter(r['understanding_level'] for r in responses)
            df_understanding = pd.DataFrame([
                {'점수': k, '학생 수': v} for k, v in sorted(understanding_dist.items())
            ])
            fig2 = px.bar(
                df_understanding,
                x='점수',
                y='학생 수',
                color='점수',
                color_continuous_scale='Blues',
                title="이해도 점수 분포"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            st.markdown("### 🆘 도움 필요 분야")
            help_dist = Counter(r['help_needed'] for r in responses if r['help_needed'] != "선택 안 함")
            if help_dist:
                df_help = pd.DataFrame([
                    {'분야': k, '요청 수': v} for k, v in help_dist.items()
                ])
                fig3 = px.pie(
                    df_help,
                    values='요청 수',
                    names='분야',
                    title="도움 요청 분야"
                )
                st.plotly_chart(fig3, use_container_width=True)
        
        # 워드클라우드 (어려웠던 부분)
        st.markdown("### ☁️ 어려웠던 부분 워드클라우드")
        difficult_texts = ' '.join([r['difficult_part'] for r in responses if r['difficult_part']])
        
        if difficult_texts.strip():
            # 한글 단어 추출
            words = re.findall(r'[가-힣]+', difficult_texts)
            word_freq = Counter(words)
            
            if word_freq:
                # 워드클라우드 생성
                wc = WordCloud(
                    font_path='/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                    background_color='white',
                    width=800,
                    height=400,
                    max_words=50,
                    relative_scaling=0.5,
                    colormap='viridis'
                ).generate_from_frequencies(word_freq)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
        
        # 데이터 다운로드
        st.markdown("### 💾 데이터 다운로드")
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV 다운로드
            df_export = pd.DataFrame([
                {
                    '날짜': r['date'],
                    '반': r['class'],
                    '번호': r['student_num'],
                    '이해도': r['understanding_level'],
                    '달성 목표 수': sum(r['goal_checks']),
                    '어려운 부분': r['difficult_part'],
                    '도움 필요': r['help_needed']
                } for r in responses
            ])
            
            csv = df_export.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv,
                file_name=f"형성평가_{st.session_state.current_date}.csv",
                mime="text/csv"
            )
        
        with col2:
            # PDF 보고서 생성 (간단한 텍스트 형식)
            report = f"""
형성평가 결과 보고서
날짜: {st.session_state.current_date}

[기본 통계]
- 응답 학생 수: {len(responses)}명
- 평균 이해도: {avg_understanding:.1f}/5.0
- 전체 목표 달성률: {achievement_rate:.1f}%

[학습 목표별 달성률]
"""
            for item in goal_achievement:
                report += f"- {item['목표 내용']}: {item['달성률']:.1f}%\n"
            
            report_bytes = report.encode('utf-8')
            st.download_button(
                label="📄 보고서 다운로드",
                data=report_bytes,
                file_name=f"형성평가_보고서_{st.session_state.current_date}.txt",
                mime="text/plain"
            )
    else:
        st.info("📢 아직 제출된 응답이 없습니다. 학생들이 응답을 제출하면 실시간으로 결과를 확인할 수 있습니다.")
    
    # 새로고침 버튼
    if st.button("🔄 결과 새로고침"):
        st.rerun()
