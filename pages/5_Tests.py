import streamlit as st
from datetime import datetime
from services.session import require_auth, sidebar_nav
from services.firebase import get_db
from services.ai_service import generate_test

st.set_page_config(page_title="Tests", page_icon="📝", layout="wide")
sidebar_nav()
user = require_auth()
db = get_db()
uid = user["uid"]
today = datetime.now().strftime("%Y-%m-%d")

st.title("📝 Tests")

test_type = st.radio("Test Type", ["daily", "weekly"], horizontal=True,
    format_func=lambda x: f"📅 Daily (Optional)" if x == "daily" else "📆 Weekly (Mandatory)")

col1, col2 = st.columns([1, 4])
with col1:
    gen = st.button("✨ Generate Test", use_container_width=True)
with col2:
    if test_type == "daily":
        if st.button("⏭️ Skip", use_container_width=False):
            st.info("Daily test skipped.")
            st.stop()

if gen:
    plan_docs = list(db.collection("plans").where("userId", "==", uid).limit(1).stream())
    if not plan_docs:
        st.error("No plan found. Create a plan first.")
        st.stop()
    plan = plan_docs[0].to_dict()
    with st.spinner("Generating test..."):
        try:
            questions = generate_test(plan["topic"], plan["level"], test_type)
            test_data = {
                "userId": uid, "type": test_type, "date": today,
                "questions": questions, "userAnswers": [], "score": None,
                "submitted": False, "createdAt": datetime.now().isoformat()
            }
            ref = db.collection("tests").add(test_data)
            st.session_state["active_test"] = {"id": ref[1].id, **test_data}
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# Show active test
if "active_test" in st.session_state and not st.session_state["active_test"].get("submitted"):
    test = st.session_state["active_test"]
    st.divider()
    st.subheader(f"{test['type'].capitalize()} Test — {len(test['questions'])} Questions")

    answers = {}
    with st.form("test_form"):
        for i, q in enumerate(test["questions"]):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            if q["type"] == "mcq" and q.get("options"):
                answers[i] = st.radio("", q["options"], key=f"q{i}", label_visibility="collapsed", index=None)
            else:
                answers[i] = st.text_input("Your answer", key=f"q{i}", label_visibility="collapsed")
            st.divider()

        submitted = st.form_submit_button("Submit Test", use_container_width=True)

    if submitted:
        user_answers = [answers.get(i, "") or "" for i in range(len(test["questions"]))]
        correct = sum(
            1 for i, q in enumerate(test["questions"])
            if user_answers[i].strip().lower() == q["answer"].strip().lower()
        )
        score = round((correct / len(test["questions"])) * 100)

        # Save to Firestore
        db.collection("tests").document(test["id"]).update({
            "userAnswers": user_answers, "score": score, "submitted": True
        })

        # Update progress
        field = "weekly_score" if test["type"] == "weekly" else "test_score"
        prog_docs = list(db.collection("progress").where("userId", "==", uid).where("date", "==", today).limit(1).stream())
        if prog_docs:
            prog_docs[0].reference.update({field: score})
        else:
            db.collection("progress").add({"userId": uid, "date": today, field: score, "daily_score": 0, "task_completion": 0})

        st.session_state["active_test"]["submitted"] = True
        st.session_state["last_score"] = {"score": score, "correct": correct, "total": len(test["questions"])}
        st.rerun()

# Show result
if "last_score" in st.session_state:
    r = st.session_state["last_score"]
    color = "green" if r["score"] >= 70 else "red"
    st.divider()
    st.markdown(f"### Score: :{color}[{r['score']}%]")
    st.markdown(f"{r['correct']} / {r['total']} correct")
    st.progress(r["score"] / 100)
    if st.button("Take Another Test"):
        del st.session_state["active_test"]
        del st.session_state["last_score"]
        st.rerun()
