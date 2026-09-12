import streamlit as st
from google import genai
import json
from datetime import date, timedelta

st.set_page_config(page_title="Whisper2Work", page_icon="✦", layout="wide")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
MODEL = "gemini-3.8-flash"

if "tasks" not in st.session_state:
    st.session_state.tasks = []


def deadline_date(text):
    t = text.lower().strip()
    today = date.today()

    if t in ["today", "tonight"]:
        return today
    if t == "tomorrow":
        return today + timedelta(days=1)
    if t == "day after tomorrow":
        return today + timedelta(days=2)
    return None


def deadline_status(d):
    if not d:
        return "No Deadline"
    today = date.today()

    if d < today:
        return "Overdue"
    if d == today:
        return "Today"
    if d == today + timedelta(days=1):
        return "Tomorrow"
    return "Upcoming"


# ---------- DESIGN ----------

st.markdown("""
<style>
.stApp {background:#080b16;}
section[data-testid="stSidebar"] {background:#0d1120;}
.stButton button {border-radius:12px;font-weight:700;}
</style>
""", unsafe_allow_html=True)


# ---------- SIDEBAR ----------

with st.sidebar:
    st.title("✦ Whisper2Work")
    st.caption("AI Productivity Assistant")
    st.divider()
    st.write("🎙️ Speak or type")
    st.write("🤖 AI understands")
    st.write("🧩 AI breaks it down")
    st.write("📅 Tracks deadlines")
    st.write("🗓️ Plans your day")
    st.write("✅ Get things done")


# ---------- HEADER ----------

st.title("✦ Whisper2Work")
st.subheader("Turn your thoughts into organized tasks.")
st.write("Type a task and let AI organize it.")
st.divider()


# ---------- CREATE TASK ----------

st.header("🎯 Create a Task")

task_text = st.text_input(
    "What do you need to do?",
    placeholder="Example: Prepare for my ML exam tomorrow"
)

if st.button("✨ Organize Task", use_container_width=True):

    if not task_text:
        st.warning("Please enter a task.")

    else:
        prompt = f"""
Analyze this task: "{task_text}"

Return ONLY JSON:
{{
"task":"short task name",
"deadline":"deadline mentioned or Not specified",
"priority":"High, Medium, or Low",
"category":"Education, Work, Personal, or Other",
"steps":["step 1","step 2","step 3"]
}}
"""

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )

            text = response.text.strip().replace("```json", "").replace("```", "")
            result = json.loads(text)

            d = deadline_date(result["deadline"])

            result["deadline_date"] = d.isoformat() if d else None
            result["completed"] = False
            result["completed_steps"] = [False] * len(result["steps"])

            st.session_state.tasks.append(result)

            st.success("✅ Task created!")

        except Exception as e:

            if "429" in str(e) or "quota" in str(e).lower():
                st.warning("⚠️ Gemini quota reached. Use Demo Tasks to test the app.")
            else:
                st.error("❌ Could not create task.")


# ---------- DEMO ----------

st.divider()
st.header("🧪 Testing Mode")

if st.button("🧪 Load Demo Tasks", use_container_width=True):

    today = date.today()

    st.session_state.tasks = [
        {
            "task": "Submit Python Assignment",
            "deadline": "Today",
            "deadline_date": today.isoformat(),
            "priority": "High",
            "category": "Education",
            "steps": ["Finish code", "Test code", "Submit"],
            "completed": False,
            "completed_steps": [False, False, False]
        },
        {
            "task": "Study Machine Learning",
            "deadline": "Tomorrow",
            "deadline_date": (today + timedelta(days=1)).isoformat(),
            "priority": "High",
            "category": "Education",
            "steps": ["Review concepts", "Practice questions", "Revise"],
            "completed": False,
            "completed_steps": [False, False, False]
        },
        {
            "task": "Prepare Resume",
            "deadline": "This Week",
            "deadline_date": (today + timedelta(days=3)).isoformat(),
            "priority": "Medium",
            "category": "Work",
            "steps": ["Update skills", "Add projects", "Review"],
            "completed": False,
            "completed_steps": [False, False, False]
        },
        {
            "task": "Organize Study Desk",
            "deadline": "Not specified",
            "deadline_date": None,
            "priority": "Low",
            "category": "Personal",
            "steps": ["Clean desk", "Arrange books", "Organize notes"],
            "completed": False,
            "completed_steps": [False, False, False]
        }
    ]

    st.success("✅ Demo tasks loaded!")


# ---------- DASHBOARD ----------

st.divider()
st.header("📊 Dashboard")

tasks = st.session_state.tasks

total = len(tasks)
completed = sum(t["completed"] for t in tasks)

c1, c2, c3 = st.columns(3)

c1.metric("📝 Total", total)
c2.metric("⏳ Pending", total - completed)
c3.metric("✅ Completed", completed)


# ---------- DEADLINE SUMMARY ----------

if tasks:

    st.subheader("📅 Deadline Summary")

    counts = {
        "Overdue": 0,
        "Today": 0,
        "Tomorrow": 0,
        "Upcoming": 0,
        "No Deadline": 0
    }

    for t in tasks:
        d = date.fromisoformat(t["deadline_date"]) if t["deadline_date"] else None
        counts[deadline_status(d)] += 1

    a, b, c, d, e = st.columns(5)

    a.metric("🔴 Overdue", counts["Overdue"])
    b.metric("🟠 Today", counts["Today"])
    c.metric("🟡 Tomorrow", counts["Tomorrow"])
    d.metric("🔵 Upcoming", counts["Upcoming"])
    e.metric("⚪ No Deadline", counts["No Deadline"])


# ---------- SEARCH / FILTER ----------

if tasks:

    st.divider()
    st.header("📝 Your Tasks")

    a, b, c = st.columns(3)

    with a:
        search = st.text_input("🔎 Search")

    with b:
        priority = st.selectbox(
            "🔥 Priority",
            ["All", "High", "Medium", "Low"]
        )

    with c:
        deadline_filter = st.selectbox(
            "📅 Deadline",
            ["All", "Overdue", "Today", "Tomorrow", "Upcoming", "No Deadline"]
        )

    sort = st.selectbox(
        "↕️ Sort Tasks",
        ["Earliest Deadline", "Latest Deadline", "Newest"]
    )

    filtered = []

    for i, t in enumerate(tasks):

        d = date.fromisoformat(t["deadline_date"]) if t["deadline_date"] else None
        status = deadline_status(d)

        if search and search.lower() not in t["task"].lower():
            continue

        if priority != "All" and t["priority"] != priority:
            continue

        if deadline_filter != "All" and status != deadline_filter:
            continue

        filtered.append((i, t))


    if sort == "Earliest Deadline":
        filtered.sort(
            key=lambda x: date.fromisoformat(x[1]["deadline_date"])
            if x[1]["deadline_date"] else date.max
        )

    elif sort == "Latest Deadline":
        filtered.sort(
            key=lambda x: date.fromisoformat(x[1]["deadline_date"])
            if x[1]["deadline_date"] else date.min,
            reverse=True
        )

    else:
        filtered.sort(key=lambda x: x[0], reverse=True)


    # ---------- DISPLAY ----------

    for i, t in filtered:

        with st.container(border=True):

            st.subheader(
                ("✅ " if t["completed"] else "📝 ") + t["task"]
            )

            d = date.fromisoformat(t["deadline_date"]) if t["deadline_date"] else None
            status = deadline_status(d)

            x, y, z = st.columns(3)

            with x:
                st.write("📅 **Deadline**")
                st.write(t["deadline"])
                st.caption(status)

            with y:
                st.write("🔥 **Priority**")
                st.write(t["priority"])

            with z:
                st.write("📚 **Category**")
                st.write(t["category"])


            if t["steps"]:

                st.write("🧩 **AI Suggested Steps**")

                for j, step in enumerate(t["steps"]):

                    t["completed_steps"][j] = st.checkbox(
                        step,
                        value=t["completed_steps"][j],
                        key=f"step_{i}_{j}"
                    )


                done = sum(t["completed_steps"])
                st.progress(done / len(t["steps"]))
                st.caption(f"{done}/{len(t['steps'])} steps completed")


            if not t["completed"]:

                if st.button(
                    "✅ Complete Task",
                    key=f"complete_{i}",
                    use_container_width=True
                ):
                    t["completed"] = True
                    st.rerun()

            if st.button(
                "🗑️ Delete",
                key=f"delete_{i}",
                use_container_width=True
            ):
                st.session_state.tasks.pop(i)
                st.rerun()


# ---------- CLEAR ----------

if tasks:

    st.divider()

    if st.button("🗑️ Clear All Tasks", use_container_width=True):
        st.session_state.tasks = []
        st.rerun()


st.divider()
st.caption("✦ Whisper2Work • Speak less. Organize more.")