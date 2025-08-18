import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import seaborn
#import plotly.graph_objects as go
import os
import warnings
warnings.filterwarnings("ignore")
st.set_page_config(page_title="Tableaux de bord Superstore!!!",page_icon=":bar_chart",layout="wide")
st.title(":bar_chart: Sample SuperStore EDA")
st.markdown('<style>div.block-container{paddy-top:1rem;}</style>', unsafe_allow_html=True)
#upload data
fl=st.file_uploader(":File_folder: Upload a file", type=(["csv", "xlsx", "xls", "txt"]))
if fl is not None:
    filename= fl.name
    st.write(filename)
    df= pd.read_excel(filename) 
else:
    os.chdir(r"C:/Users/LENOVO/Desktop/Formation Streamlit/DASH")
    df=pd.read_excel("Superstore.xls")
col1, col2 = st.columns(2)
df['Order Date'] = pd.to_datetime(df['Order Date'])

#Get the min and max date
starDate= pd.to_datetime(df['Order Date'].min())
endDate= pd.to_datetime(df['Order Date'].max())
with col1:
    date1= pd.to_datetime(st.date_input("Start Date", starDate))
with col2:
    date2= pd.to_datetime(st.date_input("End Date", endDate))
#Filter the data based on the selected date range
df= df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy( )
st.sidebar.header("Choose your filters")
#Create for region
region= st.sidebar.multiselect("Pick your Region", df['Region'].unique())
if not region:
    df2= df.copy()
else:
    df2= df[df['Region'].isin(region)]

#Create for state
state= st.sidebar.multiselect("Pick your State", df2['State'].unique())
if not state:
    df3= df2.copy()
else:
    df3= df2[df2['State'].isin(state)]

# Create for city
city = st.sidebar.multiselect("Pick your City", df3['City'].unique())

# Filter data based on region, state and city
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df['Region'].isin(region)]
elif not region and not city:
    filtered_df = df[df['State'].isin(state)]
elif state and city:
    filtered_df = df3[df3['State'].isin(state) & df3['City'].isin(city)]
elif region and city:
    filtered_df = df3[df3['Region'].isin(region) & df3['City'].isin(city)]
elif region and state:
    filtered_df = df3[df3['Region'].isin(region) & df3['State'].isin(state)]
elif city:
    filtered_df = df3[df3['City'].isin(city)]
else:
    filtered_df = df3[df3['Region'].isin(region) & df3['State'].isin(state) & df3['City'].isin(city)]
category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig= px.bar(category_df, x="Category", y="Sales",text= ['${:.2f}'.format(x) for x in category_df['Sales']],template="seaborn") 
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Region wise Sales")
    fig=px.pie(filtered_df, names="Region", values="Sales", hole=0.5)
    fig.update_traces(text= filtered_df["Region"],textposition='outside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap='Blues'))
        csv=category_df.to_csv( index=False).encode('utf-8')
        st.download_button("Download Category Data", csv, "category_data.csv", "text/csv", help='Click here to download the data')

with cl2:
    with st.expander("Region_ViewData"):
        region= filtered_df.groupby(by=["Region"], as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap='Oranges'))
        csv=filtered_df.to_csv( index=False).encode('utf-8')
        st.download_button("Download Region Data", csv, "Region_data.csv", "text/csv", help='Click here to download the data')


filtered_df["month_year"]= filtered_df["Order Date"].dt.to_period("M")
#filtered_df["month_year"] = pd.to_datetime(filtered_df["month_year"])
st.subheader("Timeseries Analysis")
linechart = (
    filtered_df
    .groupby(filtered_df["month_year"].dt.strftime("%Y: %b"))["Sales"]
    .sum()
    .reset_index()
)
fig2= px.line(linechart, x="month_year", y="Sales", labels= {"Sales":"Amount"}, height=500, width= 1000,template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of Timeseries Analysis"):
    # Affichage avec style
    st.dataframe(linechart.style.background_gradient(cmap='Greens'))
    
    # Préparer le CSV à partir du DataFrame brut
    csv = linechart.to_csv(index=False).encode('utf-8')
    
    # Bouton de téléchargement
    st.download_button(
        label="Download Timeseries Data",
        data=csv,
        file_name="Timeseries_data.csv",
        mime="text/csv",
        help='Click here to download the data'
    )

# Créer un treemap basé sur Region, Category, Sub-Category
st.subheader("Hierarchical view of sales using TreeMap")

fig3 = px.treemap(
    filtered_df,
    path=["Region", "Category", "Sub-Category"],
    values="Sales",
    color="Sub-Category",
    hover_data=["Sales"]
)

fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2= st.columns((2))
with chart1:
    st.subheader("Segment wise Sales")
    fig = px.pie(filtered_df, names="Segment", values="Sales", template="plotly_dark")
    fig.update_traces(text= filtered_df["Category"], textposition='inside')
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Category wise Sales")
    fig = px.pie(filtered_df, names="Category", values="Sales", template="gridon")
    fig.update_traces(text= filtered_df["Category"], textposition='inside')
    st.plotly_chart(fig, use_container_width=True)  

import plotly.figure_factory as ff
st.header(":Point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample=df[0:5][["Region", "State", "City", "Category", "Sales", "Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("Month wise Sub-Category Table")
filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
sub_category_year= pd.pivot_table(data=filtered_df,values="Sales", index=["Sub-Category"], columns="month")
st.write(sub_category_year.style.background_gradient(cmap='Purples'))


#nuage de point
data1= px.scatter(filtered_df, x="Sales", y="Profit", color="Sub-Category", size="Quantity")
data1["layout"].update(
    title=dict(
        text="Relationship between Sales and Profit using Scatter Plot",
        font=dict(size=20)
    ),
    xaxis=dict(
        title=dict(
            text="Sales",
            font=dict(size=19)
        )
    ),
    yaxis=dict(
        title=dict(
            text="Profit",
            font=dict(size=19)
        )
    )
)

st.plotly_chart(data1, use_container_width=True)
with st.expander("View Data of Scatter Plot"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap='Reds'))

st.page_link("Adidas_DASH.py", label="Allez à la page Adidas") # naviguer entre les pages
                      
                    