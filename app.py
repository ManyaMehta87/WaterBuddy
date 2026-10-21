"""
WaterBuddy - Your Daily Hydration Companion
FA-2: Developing and Deploying App Using Python (Streamlit)

How the file is organised:
    1. Settings and data      (age groups, tips, milestones)
    2. Calculation functions  (pure Python, easy to test)
    3. Session state setup    (the app's memory)
    4. Action functions       (what the buttons do)
    5. Display functions      (each part of the screen)
    6. main()                 (puts everything together)
"""

import random
import time
from datetime import datetime

import streamlit as st

# ----------------------------------------------------------------------
# 1. SETTINGS AND DATA
# ----------------------------------------------------------------------

# age group -> (suggested daily goal in ml, short friendly note)
AGE_GROUPS = {
    "6 - 12 years": (1600, "Growing bodies need plenty of water, so keep a bottle nearby at school!"),
    "13 - 18 years": (2000, "Busy teens do better with water: it helps focus, mood and sport."),
    "19 - 50 years": (2500, "A steady sip through the day keeps your energy up."),
    "51 - 64 years": (2300, "Thirst signals can get weaker with age, so drink on a schedule."),
    "65+ years": (2000, "Little and often works best. Don't wait until you feel thirsty."),
}

ML_PER_CUP = 240        # one metric cup
QUICK_SIP_ML = 250      # the "+250 ml" button
BOTTLE_MAX_ML = 5000    # safety limit for a single entry

HYDRATION_TIPS = [
    "Start your morning with a glass of water before tea, coffee or juice.",
    "Keep a bottle on your desk. If you can see it, you'll drink it.",
    "Fruits like watermelon, oranges and cucumber also count towards your water.",
    "Feeling tired in the afternoon? You might just be thirsty.",
    "Drink a glass of water before each meal.",
    "Pale yellow urine is a good sign that you are well hydrated.",
    "Drink more when it is hot, or when you exercise.",
    "Set small goals: one glass by 10 am, another by lunch.",
]

# (percent reached, message) - checked from the highest to the lowest
MILESTONES = [
    (100, "Goal reached! You are a hydration hero today."),
    (75, "Almost there! Just a few more glasses to go."),
    (50, "Great! You reached 50%. Halfway there!"),
    (25, "Nice start! 25% done, keep sipping."),
    (1, "First sip logged. Every drop counts."),
    (0, "Your bottle is empty. Let's drink some water!"),
]


# ----------------------------------------------------------------------
# 2. CALCULATION FUNCTIONS
# ----------------------------------------------------------------------

def total_intake(log):
    """Add up every amount (ml) in the log."""
    return sum(entry["ml"] for entry in log)


def remaining_water(goal, total):
    """How much is left to drink. Never goes below zero."""
    return max(goal - total, 0)


def percent_of_goal(total, goal):
    """Percentage of the goal that is done (can go above 100)."""
    if goal <= 0:
        return 0
    return round(total / goal * 100)


def get_milestone_message(percent):
    """Pick the right message for the current percentage."""
    for limit, message in MILESTONES:
        if percent >= limit:
            return message
    return MILESTONES[-1][1]


def mascot_for(percent):
    """Mascot emoji and mood that changes as you drink."""
    if percent >= 100:
        return "🥳", "Celebrating!"
    if percent >= 75:
        return "😄", "Super happy"
    if percent >= 50:
        return "😊", "Happy"
    if percent >= 25:
        return "🙂", "Getting better"
    return "😟", "Thirsty"


def cups_to_ml(cups):
    return cups * ML_PER_CUP


def ml_to_cups(ml):
    return ml / ML_PER_CUP


# ----------------------------------------------------------------------
# 3. SESSION STATE (the app's memory)
# ----------------------------------------------------------------------
# Streamlit re-runs the whole script after every click. Anything we want
# to remember between clicks has to live in st.session_state.

def setup_state():
    defaults = {
        "log": [],                          # list of {"time": "10:30", "ml": 250}
        "age_group": "19 - 50 years",
        "goal": AGE_GROUPS["19 - 50 years"][0],
        "tip": random.choice(HYDRATION_TIPS),
        "reminder_on": True,
        "reminder_minutes": 20,
        "last_reminder": time.time(),
        "last_milestone": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ----------------------------------------------------------------------
# 4. ACTION FUNCTIONS (used by the buttons)
# ----------------------------------------------------------------------

def add_water(amount):
    """Save one drink in the log."""
    st.session_state.log.append(
        {"time": datetime.now().strftime("%H:%M"), "ml": int(amount)}
    )


def undo_last():
    if st.session_state.log:
        st.session_state.log.pop()


def reset_day():
    """Start fresh: empty the log and pick a new tip."""
    st.session_state.log = []
    st.session_state.last_milestone = 0
    st.session_state.tip = random.choice(HYDRATION_TIPS)


def on_age_change():
    """When the age group changes, update the goal to the new suggestion."""
    st.session_state.goal = AGE_GROUPS[st.session_state.age_group][0]


def use_suggested_goal():
    st.session_state.goal = AGE_GROUPS[st.session_state.age_group][0]


def new_tip():
    st.session_state.tip = random.choice(HYDRATION_TIPS)


# ----------------------------------------------------------------------
# 5. DISPLAY FUNCTIONS
# ----------------------------------------------------------------------

def apply_style():
    """Calm aqua / blue theme and the CSS for the water bottle."""
    st.markdown(
        """
        <style>
        .stApp { background: linear-gradient(180deg, #e8f7fb 0%, #ffffff 60%); }
        h1, h2, h3 { color: #0b5d7a; }
        div.stButton > button {
            background-color: #0e87b0;
            color: white;
            border-radius: 10px;
            border: none;
            font-size: 1.05rem;
            padding: 0.6rem 1rem;
        }
        div.stButton > button:hover { background-color: #0b6d8d; color: white; }
        .bottle-wrap { display: flex; justify-content: center; }
        .bottle-neck {
            width: 46px; height: 22px; margin: 0 auto;
            background: #cfeaf3; border: 3px solid #0b5d7a; border-bottom: none;
            border-radius: 8px 8px 0 0;
        }
        .bottle {
            position: relative; width: 120px; height: 260px;
            border: 3px solid #0b5d7a; border-radius: 22px 22px 30px 30px;
            background: #f3fbfd; overflow: hidden;
        }
        .water {
            position: absolute; bottom: 0; left: 0; width: 100%;
            background: linear-gradient(180deg, #4fc3e8, #0e87b0);
            transition: height 0.8s ease;
        }
        .bottle-label {
            position: absolute; top: 45%; width: 100%; text-align: center;
            font-size: 1.6rem; font-weight: 700; color: #08475e;
            text-shadow: 0 0 6px #ffffff;
        }
        .mascot { font-size: 4rem; text-align: center; line-height: 1.1; }
        .mood { text-align: center; color: #0b5d7a; font-weight: 600; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_bottle(percent):
    """Water bottle that fills up. Height is capped at 100%."""
    fill = min(percent, 100)
    st.markdown(
        f"""
        <div class="bottle-wrap"><div>
            <div class="bottle-neck"></div>
            <div class="bottle">
                <div class="water" style="height:{fill}%;"></div>
                <div class="bottle-label">{percent}%</div>
            </div>
        </div></div>
        """,
        unsafe_allow_html=True,
    )


def show_sidebar():
    with st.sidebar:
        st.header("Hydration corner")
        st.write("**Tip of the moment**")
        st.info(st.session_state.tip)
        st.button("Show another tip", on_click=new_tip)

        st.divider()
        st.write("**Reminder**")
        st.checkbox("Remind me to drink water", key="reminder_on")
        st.number_input(
            "Remind me every (minutes)",
            min_value=1, max_value=120, step=1, key="reminder_minutes",
        )

        st.divider()
        st.write("**Cups and millilitres**")
        mode = st.radio("Convert", ["cups to ml", "ml to cups"], horizontal=True)
        if mode == "cups to ml":
            cups = st.number_input("Cups", min_value=0.0, value=1.0, step=0.5)
            st.write(f"{cups} cup(s) = **{cups_to_ml(cups):.0f} ml**")
        else:
            ml = st.number_input("Millilitres", min_value=0, value=250, step=50)
            st.write(f"{ml} ml = **{ml_to_cups(ml):.2f} cups**")
        st.caption(f"1 cup = {ML_PER_CUP} ml")


def show_age_and_goal():
    """Step 1: age group and daily goal (suggested vs your own)."""
    st.subheader("1. About you")
    st.selectbox(
        "Choose your age group",
        list(AGE_GROUPS.keys()),
        key="age_group",
        on_change=on_age_change,
    )

    suggested, note = AGE_GROUPS[st.session_state.age_group]
    st.caption(note)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Suggested goal", f"{suggested} ml")
        st.button("Use suggested goal", on_click=use_suggested_goal)
    with col2:
        st.number_input(
            "Your daily goal (ml)",
            min_value=500, max_value=6000, step=100, key="goal",
        )
        diff = st.session_state.goal - suggested
        if diff == 0:
            st.caption("Same as the suggested goal.")
        elif diff > 0:
            st.caption(f"{diff} ml above the suggested goal.")
        else:
            st.caption(f"{abs(diff)} ml below the suggested goal.")


def show_logging():
    """Step 2: quick +250 ml button and a custom amount box."""
    st.subheader("2. Log your water")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"+ {QUICK_SIP_ML} ml", use_container_width=True):
            add_water(QUICK_SIP_ML)
            st.rerun()
    with col2:
        custom = st.number_input(
            "Or type an amount (ml)",
            min_value=0, max_value=BOTTLE_MAX_ML, value=0, step=50,
            label_visibility="visible",
        )
        if st.button("Add this amount", use_container_width=True):
            if custom > 0:
                add_water(custom)
                st.rerun()
            else:
                st.warning("Please type an amount bigger than 0.")


def show_progress(total, goal):
    """Step 3: numbers, bottle, progress bar, mascot and message."""
    st.subheader("3. Your progress")
    percent = percent_of_goal(total, goal)
    left = remaining_water(goal, total)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Drunk so far", f"{total} ml")
    col_b.metric("Still to go", f"{left} ml")
    col_c.metric("Goal done", f"{percent}%")

    bottle_col, text_col = st.columns([1, 1.4])
    with bottle_col:
        show_bottle(percent)
    with text_col:
        emoji, mood = mascot_for(percent)
        st.markdown(f'<div class="mascot">{emoji}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="mood">{mood}</div>', unsafe_allow_html=True)
        message = get_milestone_message(percent)
        if percent >= 100:
            st.success(message)
        else:
            st.info(message)
        st.progress(min(percent, 100) / 100)
        if percent > 100:
            st.caption(f"You went {total - goal} ml over your goal. That's okay, "
                       "just don't overdo it.")

    # balloons only the first time a new 100% is reached
    if percent >= 100 and st.session_state.last_milestone < 100:
        st.balloons()
    st.session_state.last_milestone = percent


def show_comparison(total, goal):
    """Optional: your goal and the standard age target side by side."""
    standard = AGE_GROUPS[st.session_state.age_group][0]
    st.subheader("4. You vs the standard target")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Standard for {st.session_state.age_group}** ({standard} ml)")
        st.progress(min(total / standard, 1.0))
        st.caption(f"{percent_of_goal(total, standard)}% of the standard target")
    with col2:
        st.write(f"**Your own goal** ({goal} ml)")
        st.progress(min(total / goal, 1.0))
        st.caption(f"{percent_of_goal(total, goal)}% of your goal")


def show_history_and_reset(total, goal):
    st.subheader("5. Today's log")
    log = st.session_state.log
    if log:
        rows = [{"Drink #": i + 1, "Time": e["time"], "Amount (ml)": e["ml"]}
                for i, e in enumerate(log)]
        st.dataframe(rows, hide_index=True, use_container_width=True)
    else:
        st.write("Nothing logged yet today.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Undo last drink", use_container_width=True):
            undo_last()
            st.rerun()
    with col2:
        if st.button("Reset for a new day", use_container_width=True):
            reset_day()
            st.rerun()

    if log:
        with st.expander("End-of-day summary"):
            percent = percent_of_goal(total, goal)
            biggest = max(e["ml"] for e in log)
            st.write(f"- Drinks logged: **{len(log)}**")
            st.write(f"- Total water: **{total} ml** ({percent}% of your goal)")
            st.write(f"- Average per drink: **{total // len(log)} ml**")
            st.write(f"- Biggest drink: **{biggest} ml**")
            if percent >= 100:
                st.success("Perfect day. You reached your goal!")
            elif percent >= 75:
                st.info("Good day. You were very close to your goal.")
            else:
                st.warning("Try to drink a bit more tomorrow. You can do it!")


# The fragment checks the clock every 30 seconds on its own, without
# re-running the whole page. When the chosen number of minutes has passed
# it pops up a toast message.
@st.fragment(run_every="30s")
def reminder_check():
    if not st.session_state.reminder_on:
        return
    gap = st.session_state.reminder_minutes * 60
    if time.time() - st.session_state.last_reminder >= gap:
        st.toast("Time for a drink! Please drink your water.", icon="💧")
        st.session_state.last_reminder = time.time()


# ----------------------------------------------------------------------
# 6. MAIN
# ----------------------------------------------------------------------

def main():
    st.set_page_config(page_title="WaterBuddy", page_icon="💧", layout="centered")
    setup_state()
    apply_style()

    st.title("💧 WaterBuddy")
    st.write("Your daily hydration companion. Pick your age, set a goal and "
             "sip your way to it.")

    show_sidebar()
    reminder_check()

    # sidebar widgets and goal box come first, so the numbers below
    # always use the newest values
    show_age_and_goal()
    st.divider()
    show_logging()
    st.divider()

    goal = st.session_state.goal
    total = total_intake(st.session_state.log)

    show_progress(total, goal)
    st.divider()
    show_comparison(total, goal)
    st.divider()
    show_history_and_reset(total, goal)

    st.caption("WaterBuddy keeps your data only in this browser session. "
               "Nothing is saved on a server.")


main()
