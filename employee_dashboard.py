# Importing library
import pandas as pd
import streamlit as st
import plotly.express as px

# set up config
st.set_page_config(
    page_title="Employee Dashboard",
    page_icon="👷‍♂️",
    layout="wide"
)


@st.cache_data
def load_dataset():
    try:
        df = pd.read_csv("employee_cleaned_dataset.csv")
        return df
    except FileNotFoundError as e:
        st.warning(f"An Error occured: {e}")


def create_sidebar_filter(df):
    st.sidebar.header("👷‍♂️Employee Filters")

    department = st.sidebar.multiselect(
        "Select Department",
        options=df["Department"].unique(),
        default=df["Department"].unique(),
    )

    location = st.sidebar.multiselect(
        "Select Location",
        options=df["Office Location"].unique(),
        default=df["Office Location"].unique(),
    )
    remote = st.sidebar.radio(
        "Select Remote(s)",
        options=["All", "Yes", "No"],
        index=0
    )
    return department, location, remote

def filter_data(df, department, location, remote):
    filtered_df = df[df["Department"].isin(department) & df["Office Location"].isin(location)]
    if remote != "All":
        filtered_df = filtered_df[filtered_df["Remote"] == remote]

    return filtered_df    

def display_metrics(filtered_df):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👤 Total Employee", len(filtered_df)

    with col2:
        avg_salary = filtered_df["Salary"].mean() if len(filtered_df) > 0 else 0
        st.metric("💲 Average Salary", f"${avg_salary:,.2f}")

    with col3:
        avg_performance = filtered_df["Performance"].mean() if len(filtered_df) > 0 else 0
        st.metric("📊 Average Perfromance", f"{avg_performance:.1f}")

    with col4:
        remote_pct = (filtered_df["Remote"] == "Yes").sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric("👤 Remote Worker", f"{remote_pct:.1f}%")

def display_chart(filtered_df):
    if len(filtered_df) == 0:
        st.warning("No filter data to display. Please adjust the data from the sidebar.")
        return
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Employee Distribution by Department")
        dept_count = filtered_df["Department"].value_counts()
        fig1 = px.pie(
            values=dept_count.values,
            names=dept_count.index,
            hole=0.4
        )
        st.plotly_chart(fig1, width="stretch")

    with col2:
        st.subheader("Average Salary by Header")
        avg_salary = filtered_df.groupby("Department")["Salary"].mean().sort_values(ascending=False)
        fig2 = px.bar(
            x=avg_salary.values,
            y=avg_salary.index
        )
        fig2.update_layout(
            xaxis_title="Salary",
            yaxis_title="Department"
        )
        st.plotly_chart(fig2, width="stretch")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Perfromance Distribution")
        fig3 = px.histogram(
            filtered_df,
            x="Performance",
            nbins=6
        )
        fig3.update_traces(
            marker_line_color="white",
            marker_line_width=1
        )
        fig3.update_layout(
            xaxis_title="Performance",
            yaxis_title="Count"
        )
        st.plotly_chart(fig3, width="content")

        with col4:
            st.subheader("Employee By Office Location")
            location_count = filtered_df["Office Location"].value_counts()
            fig4 = px.bar(
                x=location_count.index,
                y=location_count.values,
                orientation="v"
            )
            fig4.update_layout(
                xaxis_title="Office Location",
                yaxis_title="Count"
            )
            st.plotly_chart(fig4, width="content")

def display_dataframe(filtered_df):
    if len(filtered_df) > 0:
        st.dataframe(filtered_df, width="stretch", height=300)
    else:
        st.warning("No employee data to display.")

def main():
    # load dataset
    df = load_dataset()

    # sidebar
    department, location, remote = create_sidebar_filter(df)

    # filtered_df 
    filtered_df = filter_data(df, department, location, remote)

    #main_layout
    st.title("Employee Dashboard")
    st.markdown("---")

    #metrics
    display_metrics(filtered_df)

    #plotly_chart
    display_chart(filtered_df)

    #display table
    display_dataframe(filtered_df)

if __name__ == "__main__":
    main()
