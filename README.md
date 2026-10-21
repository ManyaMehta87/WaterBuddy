# 💧 WaterBuddy: Your Daily Hydration Companion

WaterBuddy is a small web app that helps you drink enough water every day. You pick your age group, it suggests a daily goal, and you log your drinks while a water bottle fills up on screen.

Built for **FA-2: Developing and Deploying App Using Python** (Python Programming, Year 1) using Python and Streamlit.

**Live app:** PASTE-YOUR-STREAMLIT-LINK-HERE

## What it does

- Choose your age group and get a suggested daily goal (for example 1600 ml for ages 6-12 and 2500 ml for ages 19-50).
- Change the goal yourself if you want, and see how it compares with the standard target.
- Log water with the **+250 ml** button, or type any amount.
- See total intake, water remaining and percentage of the goal, updated instantly.
- Watch the bottle and progress bar fill up while the mascot changes mood.
- Get a message at 25%, 50%, 75% and 100% of your goal.
- Reset the day, or undo your last drink.
- Extras: cups to ml converter, drink reminder (default every 20 minutes), random hydration tips, and an end-of-day summary.

## How it works

The code is split into small functions:

| Part | Job |
| --- | --- |
| Calculation functions | total, remaining and percent of goal |
| Action functions | add water, undo, reset |
| Display functions | each section of the screen |
| `st.session_state` | remembers your drinks between clicks |

## Run it on your own computer

1. Install Python.
2. Install Streamlit: `pip install -r requirements.txt`
3. Start the app: `streamlit run app.py`

## Files

- `app.py`: all the app code
- `requirements.txt`: the libraries the app needs

## Privacy

Nothing is saved on a server. Your drinks only stay in your browser while the page is open.

## Note

The suggested goals are general guidelines, not medical advice. Ask a doctor if you have a health condition.
