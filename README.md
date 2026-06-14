# Student Analytics Dashboard

A six-page Streamlit application that turns the Kayfa platform's raw multi-source
student data into an interactive view of platform health, group performance,
academic outcomes, curriculum weak spots, behavioural drivers, and at-risk
students. All heavy analytics are precomputed in a Jupyter notebook and pushed
to **MongoDB Atlas**; the dashboard reads ready-made results from Atlas rather
than recomputing from raw files on every load.

> **Built by Eng. Rahma Saber** as part of the Kayfa Data Analytics
> internship — Month 1 Evaluation, Task 2.

Demo link :https://studentpreformanceanalysis-kayfa-task2.streamlit.app/
---

## What it does

- Answers all 15 evaluation questions through 25+ Plotly visualizations
  with Insight + Recommended Action cards under each chart.
- Provides six global sidebar filters — **Group, Course, Age Band, Gender,
  Segment, Instructor** — that subset the charts in real time.
- bcrypt-backed login against an Atlas `users` collection.
- Custom design system with a navy hero banner, Kayfa branding, and
  consistent insight/CTA cards throughout.

## Pages

| Page          | What it answers                                    |
| ------------- | -------------------------------------------------- |
| 📊 Overview   | How healthy is the platform overall?               |
| 👥 Groups     | How are the cohorts performing relative to each other? |
| 📝 Performance| Where do students perform well, where do they lag, and why? |
| 🎯 Concepts   | Which curriculum concepts are the weak spots?      |
| 📈 Engagement | How does behavior predict outcome, and what shifted in March 2026? |
| 🚨 At Risk    | Who needs intervention, and where is risk concentrated? |

## Tech stack

- **Frontend**: Streamlit (multi-page) + custom CSS
- **Charts**: Plotly
- **Data store**: MongoDB Atlas (18 precomputed collections)
- **Auth**: bcrypt
- **Notebook**: Python · Pandas · NumPy · scikit-learn (K-Means)

## Project structure

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # paste your MONGO_URI inside
streamlit run app.py
```

**Default login:** `Kayfa_HR` / `kayfa2026@`

## Deploy on Streamlit Community Cloud

1. Push this folder to a public GitHub repo.
2. Connect at [share.streamlit.io](https://share.streamlit.io) — main file: `app.py`.
3. **Settings → Secrets**:
```toml
   MONGO_URI = "mongodb+srv://USER:PASSWORD@cluster.mongodb.net/..."
```
4. In Atlas, **Network Access** → add `0.0.0.0/0` (Streamlit Cloud has no fixed IPs).

## Atlas collections consumed

`kpi_overview` · `filter_options` · `users` · `master` · `student_segments` ·
`cluster_profiles` · `at_risk` · `group_attendance` · `group_sizes` ·
`grade_trends` · `group_merge_recommendation` · `monthly_attendance` ·
`monthly_engagement` · `course_stats` · `type_stats` ·
`late_submission_impact` · `concept_failures` · `concept_mastery_timeline`.

---

**Author:** Eng. Rahma Saber
Kayfa AI & Data Analytics Internship · Month 1 Evaluation · Data Analytics Track
