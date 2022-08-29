import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import asyncio
import pickle
import streamlit_authenticator as stauth
import asyncio
import re
from PIL import Image
from pathlib import Path
img=Image.open('images/Sartorius_Logo.jpg')
st.set_page_config( page_title='Indicator survey',
                                page_icon=img,
                                )


image = Image.open('images/Sartorius_Logo.jpg')
image = image.resize((1000, 600))

st.image(image)

#---------User authentification

names=["Peter Parker","Rebecca Miller"]
    #--user authen
usernames=["asma","karim"]

    #----load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pk"
with file_path.open("rb") as file:
    hashed_passwords=pickle.load(file)
authenticator = stauth.Authenticate(names,usernames,hashed_passwords,"Indicator_dashboard" ,"abcdef",cookie_expiry_days=30)
name, authentication_status , username = authenticator.login("login",'main')
if authentication_status == False:
    st.error("Username/passwor is incorrect")
if authentication_status == None:
    st.warning("please enter your username and passwords")
if authentication_status :
        ### --- LOAD DATAFRAME
        col1, col2 = st.columns(2)

        with col1:
            st.header('Indicator Dashboard')

        with col2 :
             authenticator.logout("logout")

        def get_data() -> pd.DataFrame:
            uploaded_file = st.file_uploader("Choose a file")
            if uploaded_file is not None:
                df= pd.read_excel(uploaded_file,'Results')
                dg= pd.read_excel(uploaded_file,'Raw_DATA')
            return df, dg


        async def g() -> pd.DataFrame:
                df=await get_data()
                df=df.transpose()
                return  df
        #-------------------- make the page wait until loading dataframe


        #transform the first dataframe
        def transform_dataframe(df)->pd.DataFrame:
            df=df.transpose()
            df.rename(columns=df.iloc[0])
            df['years'] = df.index
            df=df.drop(index=df.index[0],
                axis=0)
            return df
        #transform the second dataframe

        def transform_second_dataframe(dg)->pd.DataFrame:
            dt= pd.DataFrame()
            dt = dg
            dt = dt.iloc[2: , :]
            dt= dt.rename(columns=dt.iloc[0])
            dt = dt.iloc[1: , :]
            dt = dt.reset_index(drop=True)
            dt["Year"] = dt["Year"].ffill()
            dt["Month"] = dt["Month"].ffill()
            dt["Week"] = dt["Week"].ffill()
            dt["Date"] = dt["Date"].ffill()
            df2=dt.fillna(value=0)
            df2['Week']=df2['Week'].astype('int')
            df2['Activity']=df2['Activity'].astype(str)
            df2=df2.sort_values(by=['Activity'])
            activities=df2['Activity'].unique().tolist()
            df2['Duration']=df2['Duration'].astype(str)
            df2['Duration']=df2['Duration'].str.replace('00', '')
            df2['Duration']=df2['Duration'].str.replace(':', '')
            df2['Duration']=df2['Duration'].astype('int')
            df2.groupby(['Year','Week','Activity'])['Duration'].sum()
            return df2

        def create_second_data(df2)-> pd.DataFrame:

            weeks_sum=df2.groupby(['Year','Week','Activity'])[['Duration']].sum().reset_index()
            weeks_sum=weeks_sum[weeks_sum['Activity']!='0']
            non_technical=df2[df2['Activity']=='0']
            non_technical=non_technical.groupby(['Year','Week','Task']).agg({'Duration':'sum'}).reset_index()
            return weeks_sum, non_technical

        def create_figure_of_non_technical_data(non_technical):

            w=non_technical['Duration'].to_list()
            k=[]
            for i in range (0, len(w)) :
               k.append(w[i]/60)
            non_technical['Duration']=k
            new_title = '<p style="font-family:sans-serif; color:black; font-size: 30px;">Non Technical Data table :</p>'
            st.markdown(new_title, unsafe_allow_html=True)
            fig = go.Figure(data=[go.Table(header=dict(values=['year','Week','Task','Duration (in hours)']),
                             cells=dict(values=[non_technical['Year'],non_technical['Week'],non_technical['Task'],non_technical['Duration']
                                        ],
                                       line_color='darkslategray',
                                       fill_color='lightcyan',

                                       font=dict(color='black', size=12),
                                       align='left'))])
            fig.update_layout(

                width=1000, height=800,)
            fig.update_xaxes(title_font_family="Arial")
            fig.update_yaxes(title_font_family="Arial")
            st.write(fig)
            new_title = '<p style="font-family:sans-serif; color:black; font-size: 30px;">Non Technical Data figure :</p>'
            st.markdown(new_title, unsafe_allow_html=True)
            non_technical['Year']=non_technical['Year'].astype(str)
            non_technical['Week']=non_technical['Week'].astype(str)
            non_technical["Year&Week"] = non_technical["Year"] + "/" + non_technical["Week"]

            fig = go.Figure([go.Scatter(x=non_technical['Year&Week'], y=non_technical['Duration'],line_color='#ffe476')])
            fig.update_layout(
                
                yaxis_title="Hour",
                xaxis_title="Date",
                width=1000, height=800,
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1,
                                 label="1m",
                                 step="month",
                                 stepmode="backward"),
                            dict(count=6,
                                 label="6m",
                                 step="month",
                                 stepmode="backward"),
                            dict(count=1,
                                 label="YTD",
                                 step="year",
                                 stepmode="todate"),
                            dict(count=1,
                                 label="1y",
                                 step="year",
                                 stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(

                        visible=True
                    )
                )
                )
            fig.update_xaxes(title_font_family="Arial")
            fig.update_yaxes(title_font_family="Arial")

            st.write(fig)

        def create_figure_of_activities(weeks_sum):

            w=weeks_sum['Duration'].to_list()

            k=[]
            for i in range (0, len(w)) :
               k.append(w[i]/60)

            weeks_sum['Duration']=k
            weeks_sum['Year']=weeks_sum['Year'].astype(str)
            weeks_sum['Week']=weeks_sum['Week'].astype(str)
            weeks_sum["Year&Week"] = weeks_sum["Year"] + "/" + weeks_sum["Week"]
            w=weeks_sum['Activity'].unique().tolist()
            dct={item: weeks_sum[weeks_sum['Activity']==item] for key,item in enumerate(w) }

            #dct.get('MFG').insert(loc=len(dct.get('MFG').columns), column='Average', value=10)
            dq={'CTO':5,'ETO':10,'MFG':6, 'PLCM':10, 'STD':8}
            for key,val in dq.items() :
                dct.get(key).insert(loc=len(dct.get(key).columns), column='Average', value=val)


            for i in w :
                new_title = f'<p style="font-family:sans-serif; color:black; font-size: 30px;"> {i} figure :</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x= dct.get(i)['Year&Week'],
                    y= dct.get(i)['Duration'],
                    mode='lines',
                    name='Total worked on a week',
                    line_color='#ffe476'))

                fig.add_trace(go.Scatter(
                    x= dct.get(i)['Year&Week'],
                    y= dct.get(i)["Average"],
                                    mode='markers', name='Theorical per week'))
                fig.update_layout(

                yaxis_title="Hour",
                xaxis_title="Date",
                width=1000, height=800,
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1,
                                 label="1m",
                                 step="month",
                                 stepmode="backward"),
                            dict(count=6,
                                 label="6m",
                                 step="month",
                                 stepmode="backward"),
                            dict(count=1,
                                 label="YTD",
                                 step="year",
                                 stepmode="todate"),
                            dict(count=1,
                                 label="1y",
                                 step="year",
                                 stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(

                        visible=True
                    )
                ))
                fig.update_xaxes(title_font_family="Arial")
                fig.update_yaxes(title_font_family="Arial")


                st.write(fig)

        # --- STREAMLIT SELECTION
        class corp_app :

            def __init__(self,df):

                df.self=df

           #create the right darafarame
            @classmethod
            def create_data(self,df)-> pd.DataFrame:
               data = pd.DataFrame()
               data['years'] = df.self['years']
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
               data = data.iloc[1: , :]

               return data



           #----CHANGE COLUMN TYPE
            @classmethod
            def change_data_column(self,data):
               data.loc[:-1,'Total']=data.loc[:-1,'Total'].astype('float')
               #data.loc[:-1,'weeks']=data.loc[:-1,'weeks'].astype('int')
               data.loc[:-1,'years']=data.loc[:-1,'years'].astype(str)
               return data



            def create_figures(self,data):

                # --- PLOT PIE CHART
                new_title = '<p style="font-family:sans-serif; color:black; font-size: 30px;">fig theorical and total of hours worked on a week :</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data['years'], y=data['Total'],
                                    mode='lines',
                                    name='Total worked on a week',
                                    line_color='#ffe476'))

                fig.add_trace(go.Scatter(x=data['years'], y=data['Theorical per week'],
                                    mode='markers', name='Theorical per week'))

                fig.update_layout(
                    xaxis_title="weeks",
                    yaxis_title="Total",
                    legend_title="Total & theorical per week",
                    width=1000, height=500,
                    xaxis=dict(
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1,
                                     label="1m",
                                     step="month",
                                     stepmode="backward"),
                                dict(count=6,
                                     label="6m",
                                     step="month",
                                     stepmode="backward"),
                                dict(count=1,
                                     label="YTD",
                                     step="year",
                                     stepmode="todate"),
                                dict(count=1,
                                     label="1y",
                                     step="year",
                                     stepmode="backward"),
                                dict(step="all")
                            ])
                        ),
                        rangeslider=dict(

                            visible=True
                        )
                    )

                )
                fig.update_xaxes(title_font_family="Arial")
                fig.update_yaxes(title_font_family="Arial")
                st.write(fig)

                #-----------------Absnece and breaks per year&week
                new_title = '<p style="font-family:sans-serif; color:black; font-size: 30px;">Absnece and breaks per year&week :</p>'
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
                fig.update_layout(width=1000, height=800,)
                fig.update_xaxes(title_font_family="Arial")
                fig.update_yaxes(title_font_family="Arial")
                st.write(fig)

                #--------------------Non technical Data per week
                new_title = '<p style="font-family:sans-serif; color:black; font-size: 30px;">Non technical Data per week :</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                fig = px.line(data, x="years", y="Non technical Data", markers=True  )
                fig.update_layout(

                    xaxis_title="weeks",
                    yaxis_title="Non technical Data",
                    legend_title="Legend Title",

                    width=1000, height=800,
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                        color='black'

                    )
                )
                fig.update_xaxes(title_font_family="Arial")
                fig.update_yaxes(title_font_family="Arial")
                st.write(fig)

                #------------Absence per week
                new_title = '<p style="font-family:sans-serif; color:black; font-size: 30px;">Absence per week :</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                fig = px.line(data, x="years", y="Absence", markers=True)
                fig.update_layout(
                    yaxis_title="hours",
                    width=1000, height=800,)
                fig.update_xaxes(title_font_family="Arial")
                fig.update_yaxes(title_font_family="Arial")
                st.write(fig)

                #------------box plot on total
                new_title = '<p style="font-family:sans-serif; color:black; font-size: 30px;">box plot on total:</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                fig = px.box(data, y="Total")
                fig.update_xaxes(title_font_family="Arial")
                fig.update_yaxes(title_font_family="Arial")
                st.write(fig)

        def main():

            df, dg= get_data()
            df =transform_dataframe(df)
            dataframe=corp_app(df)
            data=dataframe.create_data(df)
            dataframe.change_data_column(data)
            dataframe.create_figures(data)
            dg =transform_second_dataframe(dg)
            weeks_sum,non_technical=create_second_data(dg)
            create_figure_of_non_technical_data(non_technical)
            create_figure_of_activities(weeks_sum)


        if __name__ == "__main__":
            main()
