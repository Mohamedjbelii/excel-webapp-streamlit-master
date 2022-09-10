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
from datetime import date
current_year = date.today().year

img=Image.open('images/Sartorius_Logo.jpg')
st.set_page_config( page_title=f'{current_year}   Indicator survey',
                                page_icon=img,
                                )


image = Image.open('images/Sartorius_Logo.jpg')
image = image.resize((1000, 600))

st.image(image)

#---------User authentification

names=["asma","karim","ahmed"]
    #--user authen
usernames=["asma","karim","ahmed"]

    #----load hashed passwords
file_path = Path(__file__).parent / "hashed2_pw.pk"
with file_path.open("rb") as file:
    hashed_passwords=pickle.load(file)
authenticator = stauth.Authenticate(names,usernames,hashed_passwords,"Indicator_dashboard" ,"abcdef",cookie_expiry_days=30)
name, authentication_status , username = authenticator.login("login",'main')
    #------------In case of error
if authentication_status == False:
    st.error("Username/passwor is incorrect")
if authentication_status == None:
    st.warning("please enter your username and passwords")
if authentication_status :
        col1, col2 = st.columns(2)

        with col1:
            st.header(f'Indicator Dashboard {current_year}')

        with col2 :
             authenticator.logout("logout")

    #------------Load data
        def get_data() -> pd.DataFrame:
            uploaded_file = st.file_uploader("Choose a file")
            if uploaded_file is not None:
                df= pd.read_excel(uploaded_file,'Results')
                dg= pd.read_excel(uploaded_file,'Raw_DATA',usecols='A:k')
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
            dt.drop(['PROJ. NAME'], axis=1,inplace=True)
            df2=dt.fillna(value=0)
            df2['Week']=df2['Week'].astype('int')
            df2['Activity']=df2['Activity'].astype(str)
            df2['MM/WF CODE']=df2['MM/WF CODE'].astype(str)
            df2=df2.sort_values(by=['Activity'])
            activities=df2['Activity'].unique().tolist()
            df2['Duration']=df2['Duration'].astype(str)
            df2['Duration']=df2['Duration'].str.replace('00', '')
            df2['Duration']=df2['Duration'].str.replace(':', '')
            df2['Duration']=df2['Duration'].astype('int')
            df2.groupby(['Year','Week','Activity','MM/WF CODE'])['Duration'].sum()
            current_year = date.today().year
            df2=df2[df2['Year']==current_year]
            return df2

        #------------create_second_data
        def create_second_data(df2)-> pd.DataFrame:

            weeks_sum=df2.groupby(['Year','Week','Activity','MM/WF CODE'])[['Duration']].sum().reset_index()
            weeks_sum=weeks_sum[weeks_sum['Activity']!='0']
            non_technical=df2[df2['Activity']=='0']
            non_technical=non_technical.groupby(['Year','Week','Task']).agg({'Duration':'sum'}).reset_index()
            return weeks_sum, non_technical

        #------------create_second_data_figures_of_non_technical_data
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

            non_technical['Year']=non_technical['Year'].astype(str)
            non_technical['Week']=non_technical['Week'].astype(str)



        #------------create_second_data_figures_of_activities
        def create_figure_of_activities(weeks_sum):
        #------------create_activities_dictionary
            w=weeks_sum['Duration'].to_list()
            k=[]
            for i in range (0, len(w)) :
               k.append(w[i]/60)
            weeks_sum['Duration']=k
            weeks_sum['Year']=weeks_sum['Year'].astype(str)
            weeks_sum['Week']=weeks_sum['Week'].astype(str)
            w=weeks_sum['Activity'].unique().tolist()
            dct={item: weeks_sum[weeks_sum['Activity']==item] for key,item in enumerate(w) }

        #------------Insert_average_column
            dq={'CTO':5,'ETO':10,'MFG':5, 'PLCM':5, 'STD':10}
            newdict = {k: dq[k] for k in w if k in dq}

            for key,val in newdict.items() :
                dct.get(key).insert(loc=len(dct.get(key).columns), column='Avg', value=val)

        #------------create_table_of_activities
            new_title = '<p style="font-family:sans-serif; color:black; font-size: 30px;">activities figure :</p>'
            st.markdown(new_title, unsafe_allow_html=True)
            frames=[]
            for i in w:
                 frames.append(dct.get(i))
            result = pd.concat(frames)
            st.dataframe(result)


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
                data['years'] = pd.to_numeric(data['years'])
                current_year = date.today().year
                data=data[data['years'] >= current_year]
                data['years']=round(data['years'])
                data['years']=data['years'].astype('int')


                #--------------------Non technical Data per week
                new_title = '<p style="font-family:sans-serif; color:black; font-size: 30px;">Non technical Data per week :</p>'
                st.markdown(new_title, unsafe_allow_html=True)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data['weeks'], y=data['Total'],
                    mode='lines',
                    name='Total worked on a week'))
                fig.add_trace(go.Scatter(x=data['weeks'], y=data['Theorical per week'],
                    mode='markers', name='Theorical per week'))
                fig.update_layout(

                    xaxis_title="weeks",
                    yaxis_title="Hours",
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
                fig = px.line(data, x="weeks", y="Absence", markers=True)
                fig.update_layout(
                    yaxis_title="hours",
                    width=1000, height=800,)
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
