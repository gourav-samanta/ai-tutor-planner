import streamlit as st
from datetime import datetime
from services.session import require_auth, sidebar_nav
from services.firebase import get_db
from services.ai_service import generate_test

st.set_page_config(page_title="Tests", page_icon="📝", layout="wide")

# Hide default Streamlit navigation
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

sidebar_nav()
user = require_auth()
db = get_db()
uid = user["uid"]
today = datetime.now().strftime("%Y-%m-%d")

st.title("📝 Tests")

# Calculate week number since plan started
def get_week_number():
    plan_docs = list(db.collection("plans").where("userId", "==", uid).limit(1).stream())
    if not plan_docs:
        return 0
    # For simplicity, use current week of year
    return datetime.now().isocalendar()[1]

def check_weekly_test_due():
    """Check if weekly test is due (every 7 days)"""
    week_num = get_week_number()
    # Check if weekly test exists for this week
    weekly_tests = list(db.collection("tests")
        .where("userId", "==", uid)
        .where("type", "==", "weekly")
        .where("weekNumber", "==", week_num)
        .limit(1).stream())
    return len(weekly_tests) == 0

def get_or_create_daily_test():
    """Get or create today's daily test"""
    # Check if daily test exists for today
    daily_tests = list(db.collection("tests")
        .where("userId", "==", uid)
        .where("type", "==", "daily")
        .where("date", "==", today)
        .limit(1).stream())
    
    if daily_tests:
        test_doc = daily_tests[0]
        return test_doc.reference.id, test_doc.to_dict()
    
    # Generate new daily test
    plan_docs = list(db.collection("plans").where("userId", "==", uid).limit(1).stream())
    if not plan_docs:
        return None, None
    
    plan = plan_docs[0].to_dict()
    try:
        questions = generate_test(plan["topic"], plan["level"], "daily")
        test_data = {
            "userId": uid,
            "type": "daily",
            "date": today,
            "weekNumber": get_week_number(),
            "questions": questions,
            "userAnswers": [],
            "score": None,
            "submitted": False,
            "createdAt": datetime.now().isoformat()
        }
        ref = db.collection("tests").add(test_data)
        return ref[1].id, test_data
    except Exception as e:
        st.error(f"Error generating test: {e}")
        return None, None

def create_weekly_test():
    """Create mandatory weekly test"""
    plan_docs = list(db.collection("plans").where("userId", "==", uid).limit(1).stream())
    if not plan_docs:
        return None, None
    
    plan = plan_docs[0].to_dict()
    try:
        questions = generate_test(plan["topic"], plan["level"], "weekly")
        test_data = {
            "userId": uid,
            "type": "weekly",
            "date": today,
            "weekNumber": get_week_number(),
            "questions": questions,
            "userAnswers": [],
            "score": None,
            "submitted": False,
            "createdAt": datetime.now().isoformat()
        }
        ref = db.collection("tests").add(test_data)
        return ref[1].id, test_data
    except Exception as e:
        st.error(f"Error generating weekly test: {e}")
        return None, None

# Check for mandatory weekly test
weekly_due = check_weekly_test_due()

if weekly_due:
    # MANDATORY WEEKLY TEST
    st.warning("⚠️ **Weekly Test Due!** This test is mandatory and affects your progress.")
    
    # Check if there's an active weekly test
    if "active_test" not in st.session_state or st.session_state.get("active_test", {}).get("type") != "weekly":
        with st.spinner("🔄 Generating weekly test..."):
            test_id, test_data = create_weekly_test()
            if test_id:
                st.session_state["active_test"] = {"id": test_id, **test_data}
                st.rerun()
else:
    # DAILY TEST (OPTIONAL)
    st.info("📅 **Daily Test** - Optional practice test to reinforce your learning")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("📝 Take Daily Test", use_container_width=True):
            test_id, test_data = get_or_create_daily_test()
            if test_id:
                st.session_state["active_test"] = {"id": test_id, **test_data}
                st.rerun()
    with col2:
        if st.button("⏭️ Skip for Today", use_container_width=True):
            st.success("Daily test skipped. Come back tomorrow!")
            st.stop()

# Show active test
if "active_test" in st.session_state and not st.session_state["active_test"].get("submitted"):
    test = st.session_state["active_test"]
    st.divider()
    
    test_label = "📆 Weekly Test (Mandatory)" if test['type'] == "weekly" else "📅 Daily Test (Optional)"
    st.subheader(f"{test_label} — {len(test['questions'])} Questions")

    answers = {}
    with st.form("test_form"):
        for i, q in enumerate(test["questions"]):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            if q["type"] == "mcq" and q.get("options"):
                answers[i] = st.radio("", q["options"], key=f"q{i}", label_visibility="collapsed", index=None)
            else:
                answers[i] = st.text_input("Your answer", key=f"q{i}", label_visibility="collapsed")
            st.divider()

        submitted = st.form_submit_button("✅ Submit Test", use_container_width=True)

    if submitted:
        user_answers = [answers.get(i, "") or "" for i in range(len(test["questions"]))]
        correct = sum(
            1 for i, q in enumerate(test["questions"])
            if user_answers[i].strip().lower() == q["answer"].strip().lower()
        )
        score = round((correct / len(test["questions"])) * 100)

        # Save to Firestore
        db.collection("tests").document(test["id"]).update({
            "userAnswers": user_answers,
            "score": score,
            "submitted": True,
            "submittedAt": datetime.now().isoformat()
        })

        # Update progress
        field = "weekly_score" if test["type"] == "weekly" else "daily_test_score"
        prog_docs = list(db.collection("progress").where("userId", "==", uid).where("date", "==", today).limit(1).stream())
        if prog_docs:
            prog_docs[0].reference.update({field: score})
        else:
            db.collection("progress").add({
                "userId": uid,
                "date": today,
                field: score,
                "daily_score": 0,
                "task_completion": 0
            })

        st.session_state["active_test"]["submitted"] = True
        st.session_state["last_score"] = {
            "score": score,
            "correct": correct,
            "total": len(test["questions"]),
            "type": test["type"]
        }
        st.rerun()

# Show result
if "last_score" in st.session_state:
    r = st.session_state["last_score"]
    color = "green" if r["score"] >= 70 else "orange" if r["score"] >= 50 else "red"
    st.divider()
    st.markdown(f"### 🎯 Score: :{color}[{r['score']}%]")
    st.markdown(f"✅ {r['correct']} / {r['total']} correct")
    st.progress(r["score"] / 100)
    
    if r["type"] == "weekly":
        st.success("🎉 Weekly test completed! Your progress has been updated.")
    else:
        st.info("Great job! Daily test completed.")
    
    if st.button("🏠 Back to Tests"):
        del st.session_state["active_test"]
        del st.session_state["last_score"]
        st.rerun()
