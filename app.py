import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from fpdf import FPDF

st.set_page_config(page_title="College Results Dashboard", layout="wide")

st.title("College Results Analytics Dashboard")
st.write("Analyze student performance and identify students who need attention.")

uploaded_file = st.sidebar.file_uploader(
    "Upload results.csv",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    required = [
        "Reg_No", "Name", "Dept", "CGPA",
        "Attendance", "Backlogs",
        "Subject1", "Subject2", "Subject3",
        "Subject4", "Subject5"
    ]

    missing = [col for col in required if col not in df.columns]

    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    original_count = len(df)

    df = df.drop_duplicates()

    numeric = [
        "CGPA", "Attendance", "Backlogs",
        "Subject1", "Subject2", "Subject3",
        "Subject4", "Subject5"
    ]

    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=required)

    df = df[
        (df["CGPA"].between(0, 10)) &
        (df["Attendance"].between(0, 100)) &
        (df["Backlogs"] >= 0)
    ]

    subjects = [
        "Subject1", "Subject2", "Subject3",
        "Subject4", "Subject5"
    ]

    df["Total"] = df[subjects].sum(axis=1)
    df["Percentage"] = (df["Total"] / 5).round(2)

    df["Result"] = df["Percentage"].apply(
        lambda x: "Pass" if x >= 50 else "Fail"
    )

    def risk(row):
        reasons = []

        if row["Attendance"] < 75:
            reasons.append("Low Attendance")

        if row["CGPA"] < 6.5:
            reasons.append("Low CGPA")

        if row["Backlogs"] > 2:
            reasons.append("High Backlogs")

        if row["Percentage"] < 50:
            reasons.append("Low Marks")

        return ", ".join(reasons) if reasons else "No Risk"

    df["Risk"] = df.apply(risk, axis=1)

    risk_df = df[df["Risk"] != "No Risk"]

    tab1, tab2, tab3 = st.tabs(
        ["College Overview", "Department Analysis", "At-Risk Students"]
    )

    with tab1:

        st.header("College Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Students", len(df))
        col2.metric("Average CGPA", f"{df['CGPA'].mean():.2f}")
        col3.metric(
            "Pass Percentage",
            f"{(df['Result'] == 'Pass').mean() * 100:.1f}%"
        )
        col4.metric(
            "Average Attendance",
            f"{df['Attendance'].mean():.1f}%"
        )

        st.subheader("CGPA Distribution")

        fig, ax = plt.subplots()

        sns.histplot(
            df["CGPA"],
            bins=10,
            kde=True,
            ax=ax
        )

        ax.set_xlabel("CGPA")
        ax.set_ylabel("Students")

        st.pyplot(fig)

        st.subheader("Student Data")

        st.dataframe(
            df,
            use_container_width=True
        )

    with tab2:

        st.header("Department Analysis")

        department = df.groupby("Dept").agg(
            Average_CGPA=("CGPA", "mean"),
            Average_Attendance=("Attendance", "mean"),
            Average_Backlogs=("Backlogs", "mean"),
            Students=("Reg_No", "count")
        ).round(2)

        st.dataframe(
            department,
            use_container_width=True
        )

        st.subheader("Department CGPA Comparison")

        fig, ax = plt.subplots()

        sns.barplot(
            data=df,
            x="Dept",
            y="CGPA",
            estimator="mean",
            ax=ax
        )

        ax.set_ylabel("Average CGPA")

        st.pyplot(fig)

        best = department["Average_CGPA"].idxmax()

        st.success(
            f"Best Performing Department: {best}"
        )

    with tab3:

        st.header("At-Risk Students")

        st.write(
            "Students are flagged based on attendance, CGPA, "
            "backlogs and marks."
        )

        st.metric(
            "Total At-Risk Students",
            len(risk_df)
        )

        st.dataframe(
            risk_df[
                [
                    "Reg_No",
                    "Name",
                    "Dept",
                    "CGPA",
                    "Attendance",
                    "Backlogs",
                    "Percentage",
                    "Risk"
                ]
            ],
            use_container_width=True
        )

        csv = risk_df.to_csv(index=False)

        st.download_button(
            "Download At-Risk Students",
            csv,
            "at_risk_students.csv",
            "text/csv"
        )

else:

    st.info("Upload a results.csv file to start.")

    st.subheader("Required CSV Format")

    st.code(
        """Reg_No,Name,Dept,CGPA,Attendance,Backlogs,Subject1,Subject2,Subject3,Subject4,Subject5
1001,Arun Kumar,CSE,8.5,92,0,85,78,88,90,82
1002,Priya Sharma,ECE,6.2,68,3,55,62,58,60,59
1003,Rahul Raj,IT,7.8,88,1,75,80,77,82,79"""
    )