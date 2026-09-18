import streamlit as st
from google import genai
from google.genai import types
import json
from datetime import date, timedelta

# ---------- SETUP ----------

st.set_page_config(
    page_title="Whisper2Work",
    page_icon="✦",
    layout="wide"
)

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

MODEL ="gemini-3.5-flash-lite"

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "plan" not in st.session_state:
    st.session_state.plan = []


# ---------- AI ----------

def ai(prompt, audio=None):

    content = [prompt]

    if audio:
        content.append(
            types.Part.from_bytes(
                data=audio.getvalue(),
                mime_type=audio.type
            )
        )

    response = client.models.generate_content(
        model=MODEL,
        contents=content,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
            max_output_tokens=1200
        )
    )

    return json.loads(response.text)


# ---------- CREATE TASKS ----------

def create_tasks(text="", audio=None):

    prompt = f"""
You are Whisper2Work, an AI productivity assistant.

Today is {date.today()}.

Understand the user's thought.

Turn the thought into actionable tasks.

If the user mentions several things,
create separate tasks.

For each task provide:
- task
- deadline
- deadline_date
- priority
- category
- 2 to 4 steps

Priority must be High, Medium, or Low.

Category must be Education, Work, Personal, or Other.

Return JSON only:

{{
 "tasks": [
  {{
   "task": "short task name",
   "deadline": "Today/Tomorrow/date/Not specified",
   "deadline_date": "YYYY-MM-DD or null",
   "priority": "High",
   "category": "Education",
   "steps": ["step 1", "step 2"]
  }}
 ]
}}

User thought:
{text if text else "Understand the attached voice recording."}
"""

    result = ai(prompt, audio)

    for task in result.get("tasks", []):

        task["completed"] = False

        task["completed_steps"] = [
            False for _ in task.get("steps", [])
        ]

        st.session_state.tasks.append(task)

    return len(result.get("tasks", []))


# ---------- AI DAY PLANNER ----------

def create_plan():

    pending = [
        {
            "task": t["task"],
            "deadline": t["deadline"],
            "priority": t["priority"]
        }
        for t in st.session_state.tasks
        if not t["completed"]
    ]

    if not pending:
        return []

    prompt = f"""
Create a realistic daily plan for these tasks.

Prioritize:
1. High priority
2. Earlier deadlines
3. Important unfinished work

Return JSON only:

{{
 "plan": [
  {{
   "time": "10:00 - 11:00",
   "task": "task name",
   "reason": "short reason"
  }}
 ]
}}

Tasks:
{json.dumps(pending)}
"""

    result = ai(prompt)

    return result.get("plan", [])


# ---------- DEMO DATA ----------

def load_demo():

    today = date.today()

    st.session_state.tasks = [

        {
            "task": "Finish AI Project",
            "deadline": "Today",
            "deadline_date": today.isoformat(),
            "priority": "High",
            "category": "Education",
            "steps": [
                "Finish coding",
                "Test application",
                "Update GitHub"
            ],
            "completed": False,
            "completed_steps": [False, False, False]
        },

        {
            "task": "Study Machine Learning",
            "deadline": "Tomorrow",
            "deadline_date":
                (today + timedelta(days=1)).isoformat(),
            "priority": "High",
            "category": "Education",
            "steps": [
                "Study CNN",
                "Study RNN",
                "Revise questions"
            ],
            "completed": False,
            "completed_steps": [False, False, False]
        },

        {
            "task": "Update Resume",
            "deadline": "This Week",
            "deadline_date":
                (today + timedelta(days=3)).isoformat(),
            "priority": "Medium",
            "category": "Work",
            "steps": [
                "Update skills",
                "Add projects",
                "Review resume"
            ],
            "completed": False,
            "completed_steps": [False, False, False]
        }
    ]

    st.session_state.plan = []


# ---------- DESIGN ----------

st.markdown("""
<style>

/* Main background */
.stApp {
    background: #080B14;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0D1220;
    border-right: 1px solid #1E293B;
}

/* Main headings */
h1 {
    font-size: 42px !important;
    font-weight: 800 !important;
}

h2 {
    font-weight: 750 !important;
}

h3 {
    font-weight: 700 !important;
}

/* Cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #111827;
    border: 1px solid #263449;
    border-radius: 16px;
    padding: 8px;
}

/* Buttons */
.stButton > button {
    border-radius: 12px;
    font-weight: 700;
    min-height: 44px;
    border: 1px solid #334155;
    transition: 0.2s;
}

/* Text areas */
textarea {
    border-radius: 12px !important;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: #111827;
    border: 1px solid #263449;
    padding: 16px;
    border-radius: 14px;
}

/* Divider */
hr {
    border-color: #263449;
}

/* Audio recorder */
div[data-testid="stAudioInput"] {
    border-radius: 14px;
}

/* Sidebar text */
section[data-testid="stSidebar"] p {
    color: #CBD5E1;
}

</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------

with st.sidebar:

    st.title("✦ Whisper2Work")

    st.caption("AI Productivity Assistant")

    st.divider()

    st.write("🎙️ Voice input")
    st.write("🧠 AI understanding")
    st.write("📋 Multiple tasks")
    st.write("🧩 AI task breakdown")
    st.write("📅 Deadline tracking")
    st.write("🗓️ AI Day Planner")
    st.write("⚡ Focus Mode")


# ---------- HEADER ----------

st.title("✦ Whisper2Work")

st.subheader(
    "Turn your thoughts into organized work."
)

st.write(
    "Speak or type a messy thought. "
    "AI turns it into actionable tasks."
)

st.divider()


# ==================================================
# VOICE INPUT
# ==================================================

st.header("🎙️ Speak Your Thought")

audio = st.audio_input(
    "Record your thought"
)

if audio:

    st.audio(audio)

    if st.button(
        "🧠 Convert Voice → Tasks",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "🧠 Understanding your voice..."
            ):

                count = create_tasks(
                    audio=audio
                )

            st.success(
                f"✅ {count} task(s) created!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                "Voice processing failed."
            )

            st.caption(str(e))


# ==================================================
# TEXT INPUT
# ==================================================

st.header("⌨️ Or Type Your Thought")

text = st.text_area(
    "What do you need to do?",
    placeholder=(
        "Example: I have an ML exam next Friday. "
        "I need to study CNN, RNN and revise questions."
    ),
    height=120
)

if st.button(
    "✨ Organize My Thought",
    use_container_width=True
):

    if not text.strip():

        st.warning(
            "Please enter a thought."
        )

    else:

        try:

            with st.spinner(
                "🧠 Turning your thought into tasks..."
            ):

                count = create_tasks(
                    text=text
                )

            st.success(
                f"✅ {count} task(s) created!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                "Could not organize the thought."
            )

            st.caption(str(e))


# ==================================================
# DEMO
# ==================================================

st.divider()

st.header("🧪 Demo Mode")

if st.button(
    "Load Demo Tasks",
    use_container_width=True
):

    load_demo()

    st.success(
        "✅ Demo tasks loaded!"
    )

    st.rerun()


# ==================================================
# DASHBOARD
# ==================================================

st.divider()

st.header("📊 Productivity Dashboard")

tasks = st.session_state.tasks

total = len(tasks)

completed = sum(
    t["completed"]
    for t in tasks
)

pending = total - completed

a, b, c = st.columns(3)

a.metric(
    "📝 Total",
    total
)

b.metric(
    "⏳ Pending",
    pending
)

c.metric(
    "✅ Completed",
    completed
)


# ==================================================
# AI DAY PLANNER
# ==================================================

st.divider()

st.header("🗓️ AI Day Planner")

st.write(
    "AI creates a simple plan from your pending work."
)

if st.button(
    "✨ Plan My Day",
    use_container_width=True
):

    if not tasks:

        st.warning(
            "Create tasks first."
        )

    else:

        try:

            with st.spinner(
                "🧠 Planning your day..."
            ):

                st.session_state.plan = create_plan()

        except Exception as e:

            st.error(
                "Could not create the plan."
            )

            st.caption(str(e))


for item in st.session_state.plan:

    with st.container(border=True):

        st.write(
            "⏰ **" +
            item["time"] +
            "**"
        )

        st.subheader(
            item["task"]
        )

        st.caption(
            "💡 " +
            item["reason"]
        )


# ==================================================
# FOCUS MODE
# ==================================================

st.divider()

st.header("⚡ Focus Mode")

pending_tasks = [
    (i, t)
    for i, t in enumerate(tasks)
    if not t["completed"]
]

priority_order = {
    "High": 0,
    "Medium": 1,
    "Low": 2
}

pending_tasks.sort(
    key=lambda x:
    priority_order.get(
        x[1]["priority"],
        3
    )
)

if pending_tasks:

    index, task = pending_tasks[0]

    st.success(
        "🎯 Suggested next task"
    )

    with st.container(border=True):

        st.subheader(
            "🔥 " + task["task"]
        )

        st.write(
            "Priority:",
            task["priority"]
        )

        st.write(
            "Deadline:",
            task["deadline"]
        )

        if st.button(
            "✅ Complete Focus Task",
            key="focus_task"
        ):

            task["completed"] = True

            st.rerun()

else:

    st.info(
        "🎉 No pending tasks!"
    )


# ==================================================
# SEARCH + FILTER
# ==================================================

st.divider()

st.header("📝 Your Tasks")

if tasks:

    a, b = st.columns(2)

    with a:

        search = st.text_input(
            "🔎 Search"
        )

    with b:

        priority_filter = st.selectbox(
            "🔥 Priority",
            [
                "All",
                "High",
                "Medium",
                "Low"
            ]
        )

    for i, task in enumerate(tasks):

        if (
            search
            and search.lower()
            not in task["task"].lower()
        ):
            continue

        if (
            priority_filter != "All"
            and task["priority"]
            != priority_filter
        ):
            continue

        with st.container(border=True):

            st.subheader(
                (
                    "✅ "
                    if task["completed"]
                    else "📝 "
                )
                + task["task"]
            )

            a, b, c = st.columns(3)

            a.write(
                "📅 " +
                task["deadline"]
            )

            b.write(
                "🔥 " +
                task["priority"]
            )

            c.write(
                "📚 " +
                task["category"]
            )

            st.write(
                "🧩 **AI Suggested Steps**"
            )

            steps = task.get(
                "steps",
                []
            )

            for j, step in enumerate(steps):

                task["completed_steps"][j] = (
                    st.checkbox(
                        step,
                        value=task[
                            "completed_steps"
                        ][j],
                        key=f"step_{i}_{j}"
                    )
                )

            if steps:

                done_steps = sum(
                    task["completed_steps"]
                )

                st.progress(
                    done_steps / len(steps)
                )

                st.caption(
                    f"{done_steps}/{len(steps)} "
                    "steps completed"
                )

            col1, col2 = st.columns(2)

            with col1:

                if not task["completed"]:

                    if st.button(
                        "✅ Complete",
                        key=f"complete_{i}",
                        use_container_width=True
                    ):

                        task["completed"] = True

                        st.rerun()

            with col2:

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{i}",
                    use_container_width=True
                ):

                    tasks.pop(i)

                    st.rerun()

else:

    st.info(
        "No tasks yet. "
        "Add a thought above or load Demo Tasks."
    )


# ==================================================
# CLEAR
# ==================================================

if tasks:

    st.divider()

    if st.button(
        "🗑️ Clear All Tasks",
        use_container_width=True
    ):

        st.session_state.tasks = []
        st.session_state.plan = []

        st.rerun()


st.divider()

st.caption(
    "✦ Whisper2Work • Speak less. Organize more."
)