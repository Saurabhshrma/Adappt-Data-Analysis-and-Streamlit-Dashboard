#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Reading the data
filtered_df = pd.read_excel("filtered_df.xlsx")


# Set page title
st.set_page_config(page_title="Data Analysis Dashboard", layout='wide', initial_sidebar_state='expanded')

# Add logo in the sidebar
st.sidebar.image('Adappt.png', use_column_width=True)

#Adding colours to the dashboard
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Sidebar filters 
with st.sidebar:
    st.markdown("# Filters")
    floors = ["Both Floors"] + sorted(filtered_df["floor"].unique())
    selected_floor = st.selectbox("Floor", floors)

    date_range = st.date_input("Date Range", value=(
        filtered_df["Datetime"].min().date(), filtered_df["Datetime"].max().date()))

    sensor_ids = sorted(filtered_df["sensorId"].unique())
    selected_sensor_ids = st.multiselect("Sensor IDs", sensor_ids)

    buildings = sorted(filtered_df["building"].unique())
    selected_buildings = st.multiselect("Buildings", buildings)

    desks = sorted(filtered_df["name"].unique())
    selected_desks = st.multiselect("Desks name", desks)

st.sidebar.markdown('''
---
🕊️ 
''')

# Main page Heading
st.markdown("# Occupancy Data Analysis Dashboard")

# Apply filters
f_df = filtered_df.copy()

if selected_floor != "Both Floors":
    f_df = f_df[f_df["floor"] == selected_floor]

f_df = f_df[
    (f_df["Datetime"].dt.date >= date_range[0])
    & (f_df["Datetime"].dt.date <= date_range[1])
]

if selected_sensor_ids:
    f_df = f_df[f_df["sensorId"].isin(selected_sensor_ids)]

if selected_buildings:
    f_df = f_df[f_df["building"].isin(selected_buildings)]

if selected_desks:
    f_df = f_df[f_df["name"].isin(selected_desks)]

    
# Calculate the count of unique sensorId
unique_sensor_count = f_df["sensorId"].nunique()


# Calculate the sum of peopleCount
total_people_count = int(f_df["peopleCount"].sum())


# Calculate the count of unique buildings
unique_building_count = f_df["building"].nunique()


# Display the tiles
col1, col2, col3 = st.columns(3)

col1.metric("Unique Sensor IDs", unique_sensor_count)
col2.metric("Total People Count", total_people_count)
col3.metric("Unique Buildings", unique_building_count)

# a) Average and peak people count of both floors in a chart
average_count_floor = f_df.groupby("floor")["peopleCount"].mean()
peak_count_floor = f_df.groupby("floor")["peopleCount"].max()

c1, c2 = st.columns((5, 5))
with c1:
    st.subheader("Average and Peak People Count by Floor")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=average_count_floor.index, y=average_count_floor.values, name="Average Count"))
    fig.add_trace(go.Scatter(x=peak_count_floor.index, y=peak_count_floor.values, mode="markers+lines",
                             name="Peak Count"))
    fig.update_layout(
        xaxis_title="Floor",
        yaxis_title="People Count",
    )
    st.plotly_chart(fig)

# b) Department-wise people count statistics in a donut chart
department_count = f_df.groupby("department")["peopleCount"].sum().reset_index()

with c2:
    st.subheader("Department-wise People Count")
    fig = px.pie(department_count, values="peopleCount", names="department", hole=0.5)
    st.plotly_chart(fig)

# c) Show the top 5 desks with the most consistent occupancy in a bar chart

top_desks = f_df.groupby("name").apply(lambda x: (x["peopleCount"].sum() / x["capacity"].sum()) * 100).nlargest(5).reset_index()
top_desks.rename(columns={0: "Occupancy Rate"}, inplace=True)

c3, c4 = st.columns((5, 5))
with c3:
    st.subheader("Top 5 Desks with Most Consistent Occupancy Rate")
    fig = px.bar(top_desks, x="name", y="Occupancy Rate", color="name")
    fig.update_layout(
        xaxis_title="Desks",
        yaxis_title="Occupancy Rate",
    )
    st.plotly_chart(fig)

# top_desks = f_df.groupby("name")["peopleCount"].mean().nlargest(5).reset_index()

# c3, c4 = st.columns((5, 5))
# with c3:
#     st.subheader("Top 5 Desks with Most Consistent Occupancy")
#     fig = px.bar(top_desks, x="name", y="peopleCount", color="name")
#     fig.update_layout(
#         xaxis_title="Desks",
#         yaxis_title="People Count",
#     )
#     st.plotly_chart(fig)

# d) Show overall people count trends over day of week in a zoomable line chart
count_by_day = f_df.groupby(f_df["Datetime"].dt.strftime("%Y-%m-%d %a"))["peopleCount"].sum().reset_index()

st.subheader("Overall People Count Trends by Day of Week")
fig = px.line(count_by_day, x="Datetime", y="peopleCount", labels={"Datetime": "Date", "peopleCount": "People Count"})
fig.update_layout(title="Overall People Count Trends by Day of Week")
fig.update_xaxes(rangeslider_visible=True)
fig.update_layout(width=1400)  # Adjust the width of the graph

st.plotly_chart(fig)


# e) Highlight and plot outliers in a chart
with c4:
    st.subheader("Distribution of People Count (Outliers)")
    fig = go.Figure()
    fig.add_trace(go.Box(y=f_df["peopleCount"], name="People Count"))
    fig.update_layout(yaxis_title="People Count")
    st.plotly_chart(fig)

# Heatmap of people count by day of week and time
heatmap_data = f_df.groupby([f_df["Datetime"].dt.day_name(), f_df["Datetime"].dt.hour])["peopleCount"].mean().unstack()

st.subheader("Heatmap of People Count by Day of Week and Time")
fig = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns,
    y=heatmap_data.index,
    colorscale="YlGnBu"))
fig.update_layout(width=1400)  # Adjust the width of the graph

fig.update_layout(
    xaxis_title="Hour of Day",
    yaxis_title="Day of Week",
)
st.plotly_chart(fig)


# In[ ]:




