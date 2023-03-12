#Once created the clone of GIT-HUB repository then,
#Required libraries for the program

import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import folium
import json
import os

#!git clone https://github.com/PhonePe/pulse.git

def get_input():
    #This is to direct the path to get the data as states

    path="C:/Users/D E L L/Desktop/dash/pulse/data/aggregated/transaction/country/india/state/"
    Agg_state_list=os.listdir(path)


    #This is to extract the data's to create a dataframe

    clm={'State':[], 'Year':[],'Quarter':[],'Transacion_type':[], 'Transacion_count':[], 'Transacion_amount':[]}
    for i in Agg_state_list:
        p_i=path+i+"/"
        Agg_yr=os.listdir(p_i)    
        for j in Agg_yr:
            p_j=p_i+j+"/"
            Agg_yr_list=os.listdir(p_j)        
            for k in Agg_yr_list:
                p_k=p_j+k
                Data=open(p_k,'r')
                D=json.load(Data)
                for z in D['data']['transactionData']:
                    Name=z['name']
                    count=z['paymentInstruments'][0]['count']
                    amount=z['paymentInstruments'][0]['amount']
                    clm['Transacion_type'].append(Name)
                    clm['Transacion_count'].append(count)
                    clm['Transacion_amount'].append(amount)
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    clm['Quarter'].append(int(k.strip('.json')))
    #Succesfully created a dataframe
    df=pd.DataFrame(clm)
    return df

df=get_input()
df.to_csv("phonepe.csv", index=False)

df=pd.read_csv("phonepe.csv")



# Insert the transformed data into a Sqlite database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

table_create_sql = '''
CREATE TABLE IF NOT EXISTS phonepetable (
    Year INTEGER, 
    Quarter INTEGER,
    Transacion_type VARCHAR(255),
    Transacion_count BIGINT,
    Transacion_amount BIGINT);
'''
cursor.execute(table_create_sql)

df.to_sql('phonepetable', conn, if_exists='replace', index=False)
results=cursor.execute("SELECT * FROM phonepetable")
for row in results:
    print(row)
conn.commit()


def main():
    st.title("PhonePe Pulse Data Visualization")
    st.subheader("Analyze and visualize PhonePe Pulse data")
    
    ####GRAPH1

    df = pd.read_sql_query("SELECT * FROM phonepetable", conn)

    #df = pd.read_csv("phonepe.csv")
    category = st.selectbox("Select a category", df["State"].unique())
    filtered_df = df[df["State"] == category]
    
    fig = px.bar(filtered_df, x="Transacion_type", y="Transacion_count", color="Transacion_type", title="PhonePe Pulse Data Visualization")
    st.plotly_chart(fig, use_container_width=True)

    #####GRAPH2

    st.subheader("Visualize PhonePe Pulse data by Year/Quarter")

    # Group the data by year and quarter and calculate the sum of transaction count
    df_by_year_quarter = df.groupby(['Year', 'Quarter'])['Transacion_count'].sum().reset_index()

    # Create a facet plot using Seaborn
    g = sns.FacetGrid(df_by_year_quarter, col='Year', col_wrap=2)
    g.map(sns.barplot, 'Quarter', 'Transacion_count', palette='muted')
    g.set_axis_labels('Quarter', 'Transacion_count')
    g.set_titles('{col_name}')
    st.pyplot(g)

    #####GRAPH3

    st.subheader('Transaction count over years')
    
    # Group the data by year and calculate the sum of transaction count
    df_by_year = df.groupby('Year')['Transacion_count'].sum()

    # Create a line plot
    fig, ax = plt.subplots()
    ax.plot(df_by_year.index, df_by_year.values)
    ax.set_xlabel('Year')
    ax.set_ylabel('Transaction Count')
    ax.set_title('Transaction Count over Years')

    # Display the plot in Streamlit
    st.pyplot(fig)


    ####GRAPH4

    st.subheader('Transaction Amount by State')
    # Group the data by location and calculate the sum of transaction amount
    df_by_location = df.groupby('State')['Transacion_amount'].sum()

    # Create a bar plot
    fig, ax = plt.subplots()
    ax.bar(df_by_location.index, df_by_location.values)
    ax.set_xlabel('State')
    ax.set_ylabel('Transaction Amount')
    ax.set_title('Transaction Amount by State')

    # Tilt x label by 45 degrees
    ax.set_xticklabels(df_by_location.index, rotation=90)

    # Display the plot in Streamlit
    st.pyplot(fig)

    #####GRAPH5 GEO VISUALISATION

    st.subheader('GEO VISUALISATION OF PHONEPE PULSE DATA')
    lat_long_df = pd.read_csv("merged_file.csv")

    india_map = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

    for index, row in lat_long_df.iterrows():
        tooltip = f"State: {row['State']}, Transacion Count: {row['Transacion_count']}, Transacion Amount: {row['Transacion_amount']}"
        folium.Marker([row["Latitude"], row["Longitude"]], 
                    tooltip=tooltip,
                    icon=folium.Icon(color='red', icon='info-sign')).add_to(india_map)

    # Convert folium map to html and display in Streamlit app
    
    india_map_html = india_map._repr_html_()
    #st.markdown(india_map_html, unsafe_allow_html=True)
    st_folium_chart = st.components.v1.html(india_map_html, width=700, height=500, scrolling=True)
    #st_folium_chart = st.markdown(india_map_html, width=700, height=500, scrolling=True)

    
    # Display Streamlit app
    st_folium_chart

    st.markdown("""
    Data source: [PhonePe Pulse](https://www.phonepe.com/pulse/)
    """)
    
if __name__ == "__main__":
    main()
