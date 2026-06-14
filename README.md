# Kayfa Student Analytics — Dashboard

Multi-page Streamlit dashboard backed by MongoDB Atlas. Answers all 15 evaluation
questions; charts and insights are sourced directly from the cleaning + analysis
notebook.

## Quick start (local)

```bash
# 1. install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. configure Mongo
cp .env.example .env
# edit .env → set MONGO_URI to your Atlas connection string

# 3. run
streamlit run app.py
```

Default login (set in the notebook's Atlas seed step):

- **Username:** `Kayfa_HR`
- **Password:** `kayfa2026@`

## Deploy on Streamlit Community Cloud

1. Push this folder to a public GitHub repo.
2. Connect the repo at https://share.streamlit.io
3. Main file: `app.py`
4. Add the secret in **Settings → Secrets**:
   ```toml
   MONGO_URI = "mongodb+srv://USER:[email protected]/..."
   ```
5. In Atlas, **Network Access** → add `0.0.0.0/0` (Streamlit Cloud has no fixed IPs).

## What's inside

```
kayfa_dashboard/
├── app.py                # entry point + login gate
├── auth.py               # bcrypt verify against users collection
├── db.py                 # cached MongoClient
├── config.py             # palette, paths, constants
├── assets/
│   ├── kayfa_logo.png    # logo (top-right of every page)
│   ├── favicon.ico
│   └── styles.css        # full UI stylesheet
├── components/
│   ├── injector.py       # injects styles.css
│   ├── sidebar.py        # global filters + logout
│   ├── cards.py          # KPI tiles, page header
│   ├── charts.py         # one Plotly function per question
│   └── observations.py   # Insight + CTA cards
├── pages/
│   ├── 1_📊_Overview.py    # KPIs + Q9 cohort trend
│   ├── 2_👥_Groups.py      # Q1, Q12, Q15, Q13
│   ├── 3_📝_Performance.py # Q3, Q2, Q4, Q8
│   ├── 4_🎯_Concepts.py    # Q6, Q7
│   ├── 5_📈_Engagement.py  # Q5, Q10
│   └── 6_🚨_At_Risk.py     # Q14, Q11
└── utils/
    ├── mongo.py          # generic fetch + cache
    ├── queries.py        # one function per collection
    └── helpers.py        # chart styling (matches notebook style_fig)
```

## Atlas collections consumed (18)

`kpi_overview`, `filter_options`, `users`, `master`, `student_segments`,
`cluster_profiles`, `at_risk`, `group_attendance`, `group_sizes`, `grade_trends`,
`group_merge_recommendation`, `monthly_attendance`, `monthly_engagement`,
`course_stats`, `type_stats`, `late_submission_impact`, `concept_failures`,
`concept_mastery_timeline`.

All heavy analytics are precomputed by the notebook and read directly from Atlas —
the dashboard never re-crunches raw files on load.
