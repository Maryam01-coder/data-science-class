# Importing library
import pandas as pd
import streamlit as st
import plotly.express as px

# set up config
st.set_page_config(
    page_title="Jiji Car Listings Dashboard",
    page_icon="🚗",
    layout="wide"
)


@st.cache_data
def load_dataset():
    try:
        df = pd.read_csv("cleaned_jiji_car_dataset.csv")
        return df
    except FileNotFoundError as e:
        st.warning(f"An Error occured: {e}")


def create_sidebar_filter(df):
    st.sidebar.header("Filters")

    make = st.sidebar.multiselect(
        "Select Car Brand",
        options=df["make"].unique(),
        default=df["make"].unique(),
    )

    condition = st.sidebar.multiselect(
        "Select Car Condition",
        options=df["condition"].unique(),
        default=df["condition"].unique(),
    )
    transmission = st.sidebar.multiselect(
        "Select Car Transmission",
        options=df["transmission"].unique(),
        default=df["transmission"].unique(),
    )
    year = st.sidebar.slider(
    "Select Year",
    min_value=int(df["year"].min()),
    max_value=int(df["year"].max()),
    value=(int(df["year"].min()), int(df["year"].max()))
    )
    return make, condition, transmission, year

def filter_data(df, make, condition, transmission, year):
    filtered_df = df[
        (df["make"].isin(make)) & 
        (df["condition"].isin(condition)) & 
        (df["transmission"].isin(transmission)) & 
        (df["year"] >= year[0]) &
        (df["year"] <= year[1])
    ]

    return filtered_df 

def format_price(value):
    if value >= 1000000:
        return f"₦{value / 1000000:.1f}M"
    elif value >= 1000:
        return f"₦{value / 1000:.1f}K"
    else:
        return f"₦{value:,.0f}"

def display_metrics(filtered_df):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🚘 Total Cars", len(filtered_df))

    with col2:
        avg_price = filtered_df["price"].mean() if len(filtered_df) > 0 else 0
        st.metric("💰 Average Car Price", format_price(avg_price))

    with col3:
        most_common_car = filtered_df["model"].value_counts().idxmax() if len(filtered_df) > 0 else 0
        st.metric("🚙 Most Common Car", f"{most_common_car}")

    with col4:
        foreing_used = (filtered_df["condition"] == "Foreign Used").sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric("🚗 Foreign Used Cars", f"{foreing_used:.1f}%")

def charts(filtered_df):
    if len(filtered_df) == 0:
        st.warning('No Filter Selected. Please Adjust Your Selection.')
        return

    st.subheader('Count of Cars by Car Brand')
    car_count = filtered_df["make"].value_counts()
    fig1 = px.bar(
        x=car_count.index,
        y=car_count.values,
    )
    fig1.update_layout(
        xaxis_title='Car Brand',
        yaxis_title='Frequency'
    )
    st.plotly_chart(fig1, width='stretch')

    st.subheader('Average Price by Car Brand')
    avg_price = filtered_df.groupby("make")["price"].mean()
    fig2 = px.bar(
        x=avg_price.index,
        y=avg_price.values,
    )
    fig2.update_layout(
        xaxis_title='Car Brand',
        yaxis_title='Frequency'
    )
    st.plotly_chart(fig2, width='stretch')


    st.subheader('Price Distribution by Condition')
    fig3 = px.box(
        filtered_df,
        x="condition",
        y="price",
        labels={
            "condition": "Condition",
            "price": "Price"
        }
    )
    fig3.update_layout(
        width=1000,
        height=600
    )
    st.plotly_chart(fig3, width='stretch')

    st.subheader('Distribution of Year')
    year_count = filtered_df['year'].value_counts()
    fig4 = px.histogram(
        x=year_count.index,
        y=year_count.values,
    )
    fig4.update_layout(
        xaxis_title='Year',
        yaxis_title='Cars of the Year'
    )
    st.plotly_chart(fig4, width='stretch')

    st.subheader('Year VS Price using Car Condition')
    fig5 = px.scatter(
        filtered_df,
        x="year",
        y="price",
        color="condition",
        labels={
            "year": "Year",
            "price": "Price"
        }
    )
    st.plotly_chart(fig5, width='stretch')


    st.subheader('Correlation Between Year & Car Prices') 
    # fig6 = px.density_heatmap(
    #     filtered_df,
    #     x="year",
    #     y="price",
    #     labels={
    #         "year": "Year",
    #         "price": "Price"
    #     }
    # )
    # st.plotly_chart(fig6, width="stretch") 

    correlation = filtered_df[["year", "price"]].corr()
    fig6 = px.imshow(
        correlation,
        text_auto=True,
        aspect="auto",
        labels=dict(
            x="Variable",
            y="Variable",
            color="Correlation"
        )
    )
    st.plotly_chart(fig6, width="stretch")    

def table(filtered_df):
    if len(filtered_df) > 0:
        st.dataframe(filtered_df, width='stretch', height=300)
    else:
        st.warning('No record to display. Use the filter options.')

def main():
    # load dataset
    df = load_dataset()

    # sidebar
    make, condition, transmission, year = create_sidebar_filter(df)

    # filtered_df 
    filtered_df = filter_data(df, make, condition, transmission, year)

    #main_layout
    st.title("Car Listings Dashboard")
    st.markdown("---")

    #metrics
    display_metrics(filtered_df)

    #plotly_chart
    charts(filtered_df)

    #display table
    table(filtered_df)

if __name__ == "__main__":
    main()
