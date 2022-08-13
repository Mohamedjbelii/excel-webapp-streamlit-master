import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import asyncio
from PIL import Image
import asyncio



st.set_page_config( page_title='Indicator survey',
                    page_icon="✅",
                    )
st.header('Survey Results 2021/2022')


### --- LOAD DATAFRAME
def get_data() -> pd.DataFrame:
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        df= pd.read_excel(uploaded_file,engine='odf')
    return df
df = get_data()

async def g() -> pd.DataFrame:
        df=await get_data()
        df=df.transpose()
        return df
#-------------------- make the page wait until loading dataframe

#transform dataframe
df=df.transpose()
df.rename(columns=df.iloc[0])
df['years'] = df.index
df=df.drop(index=df.index[0],
        axis=0)

#create the right darafarame
data = pd.DataFrame()

data['years'] = df['years']
data["weeks"]=df[0]
data["Absence"]=df[3]
data["breaks"]=df[5]
data["Non technical Data"]=df[2]
data["∑ Product maintenance"]=df[6]
data["∑ Product developement"]=df[12]
data["∑ Product Transfer"]=df[17]
data["∑ Technical Data"]=df[24]
data["Total"]=df[38]
data["Theorical per week"]=df[39]

data = data.reset_index(drop=True)


#----CHANGE COLUMN TYPE
data['Total']=data['Total'].astype('float')
data['weeks']=data['weeks'].astype('int')
data['years']=data['years'].astype(str)

# --- STREAMLIT SELECTION
weeks = data['weeks'].unique().tolist()

years = data['years'].unique().tolist()

weeks_selection = st.slider('weeks:',
                        min_value= min(weeks),
                        max_value= max(weeks),
                        value=(min(weeks),max(weeks)))

years_selection = st.multiselect('years:',
                                    years,
                                    default=years)

# --- FILTER DATAFRAME BASED ON SELECTION
mask = (data['weeks'].between(*weeks_selection)) & (data['years'].isin(years_selection))
number_of_result = data[mask].shape[0]
st.markdown(f'*Available Results: {number_of_result}*')

# --- GROUP DATAFRAME AFTER SELECTION
df_grouped = data[mask].groupby(by=['Total']).count()[['weeks']]
df_grouped = df_grouped.rename(columns={'Total': 'weeks'})
df_grouped = df_grouped.reset_index()


# --- PLOT BAR CHART
bar_chart = px.bar(df_grouped,
                   x='Total',
                   y='weeks',
                   text='weeks',
                   color_discrete_sequence = ['#F63366']*len(df_grouped),
                   template= 'plotly_white')
st.plotly_chart(bar_chart)

# --- DISPLAY IMAGE & DATAFRAME
col1, col2 = st.columns(2)
image = Image.open('images/Sartorius_Logo.jpg')
print(image)
col1.image(image,

        use_column_width=True)
col2.dataframe(data[mask])

# --- PLOT PIE CHART
new_title = '<p style="font-family:sans-serif; color:Pink; font-size: 30px;">fig theorical and total of hours worked on a week :</p>'
st.markdown(new_title, unsafe_allow_html=True)
fig = go.Figure()
fig.add_trace(go.Scatter(x=data['weeks'], y=data['Total'],
                    mode='lines',
                    name='Total worked on a week'))

fig.add_trace(go.Scatter(x=data['weeks'], y=data['Theorical per week'],
                    mode='markers', name='Theorical per week'))

fig.update_layout(
    xaxis_title="weeks",
    yaxis_title="Total",
    legend_title="Total & theorical per week",

)
st.write(fig)

#-----------------Absnece and breaks per year&week

new_title = '<p style="font-family:sans-serif; color:Pink; font-size: 30px;">Absnece and breaks per year&week :</p>'
st.markdown(new_title, unsafe_allow_html=True)

fig = go.Figure(data=[go.Table(header=dict(values=['years','weeks', 'Absence','breaks']),
                 cells=dict(values=[data['years'],
                                    data['weeks'],
                                    data['Absence'],
                                    data['breaks']],
                                    line_color='darkslategray',
                                    fill_color='lightcyan',
                                    align='left',
                                    font=dict(color='black', size=12),

                          ))])

st.write(fig)
#-------------------------
new_title = '<p style="font-family:sans-serif; color:Pink; font-size: 30px;">Non technical Data per week :</p>'
st.markdown(new_title, unsafe_allow_html=True)
fig = px.line(x=data['weeks'],y=data['Non technical Data'], title='Non technical Data')
fig.update_layout(

    xaxis_title="weeks",
    yaxis_title="Non technical Data",
    legend_title="Legend Title",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="RebeccaPurple"
    )
)



st.write(fig)



#------------

new_title = '<p style="font-family:sans-serif; color:Pink; font-size: 30px;">Absence per week :</p>'
st.markdown(new_title, unsafe_allow_html=True)
fig = px.line(data, x="weeks", y="Absence", markers=True)
fig.update_layout(
    yaxis_title="hours",
)
st.write(fig)

#------------
new_title = '<p style="font-family:sans-serif; color:Pink; font-size: 30px;">box plot on total:</p>'
st.markdown(new_title, unsafe_allow_html=True)
fig = px.box(data, y="Total")
st.write(fig)



#------------



fig = px.line(data, x="weeks", y='∑ Product maintenance', markers=True,title='∑ Product maintenance')

st.write(fig)


fig = px.line(data, x="weeks", y='∑ Product Transfer', markers=True,title='∑ Product Transfer')

st.write(fig)



fig = px.line(data, x="weeks", y='∑ Product developement', markers=True,title="'∑ Product developement'")
st.write(fig)
