import streamlit as st
try:
    from agno.agent import Agent
    from agno.models.openrouter import OpenRouter
except ImportError:
    import subprocess, sys
    print("📦 检测到缺少依赖 agno，正在安装…")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "agno"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    from agno.agent import Agent
    from agno.models.openrouter import OpenRouter

st.set_page_config(
    page_title="AI 饮食与健身计划助手",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0fff4;
        border: 1px solid #9ae6b4;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fffaf0;
        border: 1px solid #fbd38d;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

def display_dietary_plan(plan_content):
    with st.expander("📋 个性化饮食计划", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 计划原理")
            st.info(plan_content.get("why_this_plan_works", "暂无相关信息"))
            st.markdown("### 🍽️ 餐食安排")
            st.write(plan_content.get("meal_plan", "暂无餐食计划"))
        
        with col2:
            st.markdown("### ⚠️ 注意事项")
            considerations = plan_content.get("important_considerations", "").split('\n')
            for consideration in considerations:
                if consideration.strip():
                    st.warning(consideration)

def display_fitness_plan(plan_content):
    with st.expander("💪 个性化健身计划", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 健身目标")
            st.success(plan_content.get("goals", "暂无目标"))
            st.markdown("### 🏋️‍♂️ 训练安排")
            st.write(plan_content.get("routine", "暂无训练计划"))
        
        with col2:
            st.markdown("### 💡 专业建议")
            tips = plan_content.get("tips", "").split('\n')
            for tip in tips:
                if tip.strip():
                    st.info(tip)

def main():
    if 'dietary_plan' not in st.session_state:
        st.session_state.dietary_plan = {}
        st.session_state.fitness_plan = {}
        st.session_state.qa_pairs = []
        st.session_state.plans_generated = False

    st.title("🏋️‍♂️ AI 饮食与健身计划助手")
    st.markdown("""
        <div style='background-color: #00008B; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem; color: white;'>
        根据您的目标与喜好，为您量身定制饮食和健身计划。
        AI 将考虑您的个人情况，为您制定科学可行的健康方案。
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("🔑 API 配置")
        glm_api_key = st.text_input(
            "GLM API Key",
            type="password",
            help="请输入您的 GLM API Key 才能继续"
        )
        
        if not glm_api_key:
            st.warning("⚠️ 请输入您的 GLM API Key 才能生成计划")
            st.markdown("[点击此处获取 GLM API Key](https://bigmodel.cn/)")
            return
        
        st.success("✅ GLM API Key 已接受！")

    if glm_api_key:
        try:
            try:
                secret_key = st.secrets.get("glm_api_key")
            except Exception:
                secret_key = None

            api_key = secret_key or glm_api_key
            glm_model = OpenRouter(
                id="glm-4.5",
                base_url="https://open.bigmodel.cn/api/paas/v4/",
                api_key=api_key,
                max_tokens=16384,
                timeout=120,
            )
        except Exception as e:
            st.error(f"❌ 初始化 GLM 模型出错: {e}")
            return

        st.header("👤 我的信息")
        
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("年龄", min_value=10, max_value=100, step=1, help="请输入您的年龄")
            height = st.number_input("身高 (cm)", min_value=100.0, max_value=250.0, step=0.1)
            activity_level = st.selectbox(
                "活动水平",
                options=["久坐", "轻度活动", "中等活动", "高强度活动", "非常高强度活动"],
                help="请选择您平时的活动强度"
            )
            dietary_preferences = st.selectbox(
                "饮食偏好",
                options=["素食", "生酮饮食", "无麸质", "低碳水", "无乳制品"],
                help="选择您的饮食偏好"
            )

        with col2:
            weight = st.number_input("体重 (kg)", min_value=20.0, max_value=300.0, step=0.1)
            sex = st.selectbox("性别", options=["男", "女", "其他"])
            fitness_goals = st.selectbox(
                "健身目标",
                options=["减脂", "增肌", "提高耐力", "保持健康", "力量训练"],
                help="请选择您的主要目标"
            )

        if st.button("🎯 生成我的计划", use_container_width=True):
            with st.spinner("正在为您制定专属健康与健身方案..."):
                try:
                    dietary_agent = Agent(
                        name="饮食专家",
                        role="提供个性化饮食建议",
                        model=glm_model,
                        instructions=[
                            "根据用户提供的信息（包括饮食偏好与限制）制定详细的一日餐食计划，包括早餐、午餐、晚餐和加餐。",
                            "说明此饮食计划如何帮助用户实现目标（例如减脂、增肌等）。",
                            "确保计划内容清晰、条理分明、营养均衡。",
                            "所有内容使用中文回答。"
                        ]
                    )

                    fitness_agent = Agent(
                        name="健身专家",
                        role="提供个性化健身建议",
                        model=glm_model,
                        instructions=[
                            "根据用户目标提供个性化健身计划，包括热身、主要训练和放松环节。",
                            "解释每个训练的作用与好处。",
                            "保证计划细致可执行。",
                            "所有内容使用中文回答。"
                        ]
                    )

                    user_profile = f"""
                    年龄: {age}
                    体重: {weight}kg
                    身高: {height}cm
                    性别: {sex}
                    活动水平: {activity_level}
                    饮食偏好: {dietary_preferences}
                    健身目标: {fitness_goals}
                    """

                    dietary_plan_response = dietary_agent.run(user_profile)
                    # print(dietary_plan_response)
                    dietary_plan = {
                        "why_this_plan_works": "高蛋白、优质脂肪、适量碳水、热量均衡",
                        "meal_plan": dietary_plan_response.content,
                        "important_considerations": """
                        - 多喝水，保持充足水分
                        - 注意电解质摄入（钠、钾、镁）
                        - 通过蔬菜、水果保证膳食纤维摄入
                        - 根据身体反馈调整食量
                        """
                    }

                    fitness_plan_response = fitness_agent.run(user_profile)
                    # print(fitness_plan_response)
                    fitness_plan = {
                        "goals": "增强力量、提升耐力并保持全身健康",
                        "routine": fitness_plan_response.content,
                        "tips": """
                        - 定期记录训练进展
                        - 保证训练间的充分休息
                        - 关注动作姿势，避免受伤
                        - 持之以恒才能见到效果
                        """
                    }

                    st.session_state.dietary_plan = dietary_plan
                    st.session_state.fitness_plan = fitness_plan
                    st.session_state.plans_generated = True
                    st.session_state.qa_pairs = []

                    display_dietary_plan(dietary_plan)
                    display_fitness_plan(fitness_plan)

                except Exception as e:
                    st.error(f"❌ 出错啦: {e}")

        if st.session_state.plans_generated:
            st.header("❓ 计划答疑")
            question_input = st.text_input("请输入您想了解的问题")

            if st.button("获取回答"):
                if question_input:
                    with st.spinner("正在为您寻找最佳解答..."):
                        dietary_plan = st.session_state.dietary_plan
                        fitness_plan = st.session_state.fitness_plan

                        context = f"刚刚，你为用户推荐了一些包含饮食和健康的计划，包括：\n\n# **饮食计划:** {dietary_plan.get('meal_plan', '')}\n\n# **健身计划:** {fitness_plan.get('routine', '')}"
                        full_context = f"{context}\n\n\n# **用户问题:** {question_input}\n\n请根据你为用户推荐的饮食和健身计划，回答用户新的问题。"

                        try:
                            agent = Agent(model=glm_model, show_tool_calls=True, markdown=True)
                            run_response = agent.run(full_context)

                            if hasattr(run_response, 'content'):
                                answer = run_response.content
                            else:
                                answer = "抱歉，目前暂时无法生成回复。"

                            st.session_state.qa_pairs.append((question_input, answer))
                        except Exception as e:
                            st.error(f"❌ 获取回答时出错: {e}")

            if st.session_state.qa_pairs:
                st.header("💬 问答记录")
                for question, answer in st.session_state.qa_pairs:
                    st.markdown(f"**问题：** {question}")
                    st.markdown(f"**回答：** {answer}")

if __name__ == "__main__":
    main()