import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import base64

# ===============================
# Streamlit Config
# ===============================
st.set_page_config(
    page_title="Forus Health | Patents & Publications Dashboard",
    layout="wide"
)

# ===============================
# Base directory (folder where app.py lives)
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def p(filename):
    """Return absolute path relative to app.py's directory."""
    return os.path.join(BASE_DIR, filename)

# ===============================
# Load Patent Data
# ===============================
patent_file = p("Patent_Data.xlsx")
xls = pd.ExcelFile(patent_file)
df = pd.read_excel(xls, sheet_name="Patents_Data")

df["Application Date"] = pd.to_datetime(df["Application Date"], errors="coerce")
df["Application Year"] = df["Application Date"].dt.year
df["Grant Date"] = pd.to_datetime(df["Grant Date"], errors="coerce")

total_patents = len(df)
granted = df["Status"].str.contains("Granted", case=False, na=False).sum()
pending = df["Status"].str.contains("Pending", case=False, na=False).sum()
grant_rate = round((granted / total_patents) * 100, 1) if total_patents else 0

# ===============================
# Load Publications Data
# ===============================
pub_df = pd.read_excel(p("Publications.xlsx"))

total_publications = len(pub_df)
published = pub_df["Status"].str.contains("Published", case=False, na=False).sum()
under_review = total_publications - published

# ===============================
# Header
# ===============================
c1, c2 = st.columns([6, 1])
with c1:
    st.title("📘 FH – Patents & Publications Dashboard")
    st.caption("Patents & Publications | Executive Dashboard")
with c2:
    logo_path = p("forus-logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)

# ===============================
# KPI STYLING
# ===============================
st.markdown("""
<style>
div[data-testid="metric-container"] label {
    font-size: 20px !important;
    font-weight: 700 !important;
}
div[data-testid="metric-container"] div {
    font-size: 36px !important;
    font-weight: 800 !important;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# KPI SUMMARY
# ===============================
st.subheader("📄 Patents Summary")
p1, p2, p3, p4 = st.columns(4)
p1.metric("Total Patents", total_patents)
p2.metric("Granted", granted)
p3.metric("Pending", pending)
p4.metric("Grant Success Rate", f"{grant_rate}%")

st.divider()

st.subheader("📚 Publications Summary")
u1, u2, u3 = st.columns(3)
u1.metric("Total Publications", total_publications)
u2.metric("Published", published)
u3.metric("Under Review / Submitted", under_review)

st.divider()

# ===============================
# ROW 1: STATUS + COUNTRY
# ===============================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Patent Status Distribution")
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.pie(
        [granted, pending],
        labels=["Granted", "Pending"],
        autopct="%1.1f%%",
        startangle=90,
        textprops={'fontsize': 5},
        wedgeprops=dict(width=0.5)
    )
    ax.set_title("Granted vs Pending", fontsize=6)
    ax.axis("equal")
    st.pyplot(fig)

with col2:
    st.subheader("Geographic Coverage")
    country_counts = df["Country"].value_counts()
    fig, ax = plt.subplots(figsize=(4.5, 3))
    ax.barh(country_counts.index, country_counts.values)
    ax.set_xlabel("Patents", fontsize=9)
    ax.set_ylabel("Country", fontsize=9)
    ax.set_title("Country-wise Distribution", fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8)
    for i, v in enumerate(country_counts.values):
        ax.text(v + 0.2, i, str(v), va="center", fontsize=8)
    st.pyplot(fig)

# ===============================
# ROW 2: YEAR TREND + INVENTORS
# ===============================
col3, col4 = st.columns(2)

with col3:
    st.subheader("Filing Trend")
    yearly = df["Application Year"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(5, 2))
    ax.plot(yearly.index, yearly.values, marker="o")
    ax.set_xlabel("Year", fontsize=9)
    ax.set_ylabel("Patents Filed", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8)
    for x, y in zip(yearly.index, yearly.values):
        ax.text(x, y + 0.2, str(y), ha="center", fontsize=8)
    st.pyplot(fig)

with col4:
    st.subheader("Inventor Contribution")
    inventor_df = pd.read_excel(xls, sheet_name="Inventor_count")
    inventor_df = inventor_df.sort_values("Count", ascending=False)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.barh(inventor_df["Name"], inventor_df["Count"])
    ax.invert_yaxis()
    ax.set_xlabel("Patent Count", fontsize=9)
    ax.set_ylabel("Inventor", fontsize=9)
    ax.set_title("Top Inventors", fontsize=11, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8)
    for i, v in enumerate(inventor_df["Count"]):
        ax.text(v + 0.2, i, str(v), va="center", fontsize=8)
    st.pyplot(fig)

# ===============================
# GRANTED PATENTS – PDF ACCESS
# ===============================
st.subheader("Granted Patents – PDF Access")

pdf_folder = p("pdfs")

def get_pdf_link(path, label):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{label}.pdf">{label}</a>'

granted_df = df[df["Status"].str.contains("Granted", case=False, na=False)]

for _, row in granted_df.iterrows():
    c1, c2, c3 = st.columns([1, 2, 5])
    c1.write(row["Grant Date"].strftime("%Y-%m-%d") if pd.notna(row["Grant Date"]) else "")

    try:
        grant_no = str(int(float(row["Grant Number"])))
    except:
        grant_no = str(row["Grant Number"]).strip()

    pdf_path = os.path.join(pdf_folder, f"{grant_no}.pdf")

    if os.path.exists(pdf_path):
        c2.markdown(get_pdf_link(pdf_path, grant_no), unsafe_allow_html=True)
    else:
        c2.write(grant_no)

    c3.write(row["Short Title"])

# ===============================
# COUNTRY FILTER + TABLE
# ===============================
selected_country = st.selectbox("Select Country", options=df['Country'].dropna().unique(), index=0)
filtered_df = df[df['Country'] == selected_country]

col_header, col_link = st.columns([5, 1])
with col_header:
    st.subheader(f"Patents in {selected_country}")
with col_link:
    country_upper = selected_country.strip().upper()
    if country_upper == "INDIA":
        st.markdown('[🔍 IP India Patent Search](https://iprsearch.ipindia.gov.in/PublicSearch/)', unsafe_allow_html=True)
    elif country_upper == "USA":
        st.markdown('[🔍 USPTO Patent Search](https://patentcenter.uspto.gov/)', unsafe_allow_html=True)

filtered_df_display = filtered_df[['Application Year', 'Application No', 'Status', 'Short Title', 'Inventors']].copy()
st.dataframe(filtered_df_display)

# ===============================
# PUBLICATIONS DETAILS
# ===============================
st.divider()
st.subheader("📚 Publication Details")

for _, row in pub_df.iterrows():
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"**{row['Title']}**")
        st.caption(f"Author(s): {row['Author']}")
        st.caption(f"Publisher: {row['Publisher']}")
        link = str(row.get("Link", "")).strip()
        status = str(row.get("Status", "")).strip().lower()
        if status == "published" and link and link.lower() != "nan":
            st.markdown(f"[🔗 View Publication]({link})")
    with col2:
        st.markdown(f"**Status:** {row['Status']}")
    st.markdown("---")
