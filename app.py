import streamlit as st  # pip install streamlit #streamlit==1.22.0
import pandas as pd  # pip install pandas
import plotly.express as px  # pip install plotly-express   plotly==5.14.1
import base64  # Standard Python Module
from io import StringIO, BytesIO  # Standard Python Module
from streamlit_option_menu import option_menu
from streamlit_extras.switch_page_button import switch_page
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from predict_cost import predict
import openpyxl
import pyodbc
from calculation import * 
from algorithm import * 

# Declare Variables   
file_name="Data\\Cleaned_Data_for_Engine.xlsx"
SKU_sheet_name="List of SKUs"
F_DS_sheet_name="Distributor_P&L_Forecast"
A_DS_sheet_name = "Distributor_Actual"
F_MF_sheet_name="Manufacture_P&L Forecast"
A_MF_sheet_name="Manufacture_Actual"
extraordinary_cost=0 
writer = pd.ExcelWriter("Data\\Output.xlsx", engine='openpyxl')




#print(openpyxl.__version__)
def generate_excel_download_link(df):
    # Credit Excel: https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/5
    towrite = BytesIO()
    #df.to_excel(towrite, encoding="utf-8", index=False, header=True)  # write to BytesIO buffer
    df.to_excel(towrite, index=False, header=True)
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="data_download.xlsx">Download Excel File</a>'
    return st.markdown(href, unsafe_allow_html=True)

def download_from_output(df):
    # Credit Excel: https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/5
    towrite = BytesIO()
    #df.to_excel(towrite, encoding="utf-8", index=False, header=True)  # write to BytesIO buffer
    df.to_excel(towrite, index=False, header=True)
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="data_download.xlsx">Download Excel File</a>'
    return st.markdown(href, unsafe_allow_html=True)

def generate_html_download_link(fig):
    # Credit Plotly: https://discuss.streamlit.io/t/download-plotly-plot-as-html/4426/2
    towrite = StringIO()
    fig.write_html(towrite, include_plotlyjs="cdn")
    towrite = BytesIO(towrite.getvalue().encode())
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download="plot.html">Download Plot</a>'
    return st.markdown(href, unsafe_allow_html=True)


st.set_page_config(page_title='TP project')


with st.sidebar:
    selected = option_menu(
        menu_title = None, options = ["Upload and view Data","TP adjustments","Machine learning for fun"],
        #orientation = "horizontal"
        )



if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'sku' not in st.session_state:
    st.session_state.sku = pd.DataFrame()
if 'f_ds' not in st.session_state:
    st.session_state.f_ds = pd.DataFrame()
if 'f_mf' not in st.session_state:
    st.session_state.f_mf = pd.DataFrame()
if 'a_ds' not in st.session_state:
    st.session_state.a_ds = pd.DataFrame()
if 'a_fm' not in st.session_state:
    st.session_state.a_fm = pd.DataFrame()


if selected == "Upload and view Data":
    st.title('TP SKU calculation engine 📈')
    
    st.subheader('Please upload the Excel file')
    uploaded_file = st.file_uploader("Choose a XLSX file with column names of 'Item', 'Quarter', 'COGS', 'OP Expemses'. If you don't have a file, you can click the button to use the mock data"
        ,type='xlsx')

    use_mock = st.button("Use mock data")

    if uploaded_file:
        #st.markdown('---')
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        SKU_list = pd.read_excel(uploaded_file, sheet_name = SKU_sheet_name)
        F_DS_df = pd.read_excel(uploaded_file, sheet_name = F_DS_sheet_name)
        F_MF_df=pd.read_excel(uploaded_file, sheet_name = F_MF_sheet_name)
        A_DS_df=pd.read_excel(uploaded_file, sheet_name = A_DS_sheet_name)
        A_MF_df=pd.read_excel(uploaded_file, sheet_name = A_MF_sheet_name)

        st.session_state.df = df
        st.session_state.sku = SKU_list
        st.session_state.f_ds = F_DS_df
        st.session_state.f_mf = F_MF_df
        st.session_state.a_ds = A_DS_df
        st.session_state.a_fm =  A_MF_df

        # clean_button = st.button("Click here to clean the data!")
        # #st.write(clean_button)
        # if clean_button:
        #     st.write("Data cleaned...")
        #     st.dataframe(df)
        #     st.session_state.clean = True

    if use_mock:
        mock_dir = 'data/Cleaned_Data_for_Engine.xlsx'
        df = pd.read_excel(mock_dir)
        SKU_list = pd.read_excel(mock_dir, sheet_name = SKU_sheet_name)
        F_DS_df = pd.read_excel(mock_dir, sheet_name = F_DS_sheet_name)
        F_MF_df=pd.read_excel(mock_dir, sheet_name = F_MF_sheet_name)
        A_DS_df=pd.read_excel(mock_dir, sheet_name = A_DS_sheet_name)
        A_MF_df=pd.read_excel(mock_dir, sheet_name = A_MF_sheet_name)

        st.session_state.df = df
        st.session_state.sku = SKU_list
        st.session_state.f_ds = F_DS_df
        st.session_state.f_mf = F_MF_df
        st.session_state.a_ds = A_DS_df
        st.session_state.a_fm =  A_MF_df

        
        st.markdown('Below is the mock data')
        
    if not st.session_state.df.empty:
        df = st.session_state.df
        
        st.markdown('---')
        st.dataframe(df)


        groupby_column = st.selectbox(
                'What do you want to group by?',
                ('Item', 'Quarter'),
            )


            # -- GROUP DATAFRAME
        output_columns = ['COGS', 'OP expenses']
        df_grouped = df.groupby(by=[groupby_column], as_index=False)[output_columns].sum()

            # -- PLOT DATAFRAME
        fig = px.bar(
            df_grouped,
            x=groupby_column,
            y='COGS',
            color='OP expenses',
            color_continuous_scale=['red', 'yellow', 'green'],
            template='plotly_white',
            title=f'<b>Sales & Profit by {groupby_column}</b>'
            )
        st.plotly_chart(fig)

        st.subheader('Downloads:')
        generate_excel_download_link(df)
        
        generate_html_download_link(fig)


        # -- DOWNLOAD SECTION



if selected == "TP adjustments":

    st.title('TP SKU calculation engine 📈')
    st.subheader('View adjustments')
    #df = st.session_state["updated_df"]
    #st.dataframe(df)
    if not st.session_state.df.empty:
        df = st.session_state.df
        SKU_list = st.session_state.sku
        F_DS_df = st.session_state.f_ds
        F_MF_df = st.session_state.f_mf
        A_DS_df = st.session_state.a_ds 
        A_MF_df = st.session_state.a_fm
        



        st.markdown('Your uploaded file')
        st.dataframe(df)
        method = st.selectbox(
        "How would you like to be calculated?",
        ("TopDown Approach", "Bottom_up approach"),)
        calculate_button = st.button("Click here to caltulate!")
        #st.write(clean_button)
        if calculate_button:


            F_DS_df = F_DS_df.rename(columns={"OP expenses":"OP_expenses"})
            A_MF_df = A_MF_df.rename(columns={"Price_per_unit":"Price"})
            A_MF_df = A_MF_df.rename(columns={"Quantity(Kpcs)":"Quantity"})

            #df merge with policy
            F_DS_Policy_df =  F_DS_df.merge(SKU_list, left_on='Item', right_on='SKU', how='left')

            #Calculate sales, gp, op 
            F_DS_Policy_df=calculate_sales_gp_op_fcost(F_DS_Policy_df ,'F','DS')
            #print(F_DS_Policy_df)

            #Calculate Quarterly Figures and Change all the namings with a total infornt 
            F_DS_Quarter_Figures_df=calculate_quartery_figures(F_DS_Policy_df,'F','DS')

            #Calculate the volume and SKU Level GP Margin and OP Margin 
            F_DS_Final_df =  F_DS_Policy_df.merge(F_DS_Quarter_Figures_df, left_on='Quarter', right_on='Quarter', how='left')
            F_DS_Final_df=calculate_volume_gpm_opm(F_DS_Final_df ,'F','DS')


            #Sum everything by quarter
            #Then join back with original table
            #And calculate again 
            # print(F_DS_Quarter_Figures_df)
            # print(F_DS_Final_df)
            F_DS_Final_df.to_excel(writer,
                            sheet_name='DS_Forecast_Information')

            ############################################################################################################
            #For Actual 
            #df merge with policy

            A_DS_Policy_df =  A_DS_df.merge(SKU_list, left_on='Item', right_on='SKU', how='left')
            #print(A_DS_Policy_df)
            #
            A_DS_Policy_df = calculate_sales_gp_op_fcost(A_DS_Policy_df ,'A','DS')

            A_DS_Quarter_Figures_df=calculate_quartery_figures(A_DS_Policy_df,'A','DS')

            #Until here is the same for forecast and actual #Can summarise into one function 
            #Only for the concatenating quarter part is only for actual 

            A_DS_Final_df=calculate_YTD(A_DS_Quarter_Figures_df,'A',"DS")

            A_DS_Final_df.to_excel(writer,
                            sheet_name='DS_YTD_Information')  

            #######################################################################################################################
            #Forecast Preparation
            #Joining Forecast and Actual 
            sorted_df=create_forecast_prep_df(F_DS_Final_df,A_DS_Final_df,'DS')

            output=calculate_forecast(sorted_df,type='OM',target=0.03)
            output.to_excel(writer,
                            sheet_name='DS_Forecast_OM') 

            output=calculate_forecast(sorted_df,type='GM',target=0.09)
            output.to_excel(writer,
                            sheet_name='DS_Forecast_GM') 

            ###################################################################\
            #For manufacturer side 
            #Forecast 

            # #This one no need once we standardize the inputs 
            F_MF_df = F_MF_df.rename(columns={"OP expenses":"OP_expenses"})

            #df merge with policy
            F_MF_Policy_df =  F_MF_df.merge(SKU_list, left_on='Item', right_on='SKU', how='left')


            #Calculate sales, gp, op 
            F_MF_Policy_df=calculate_sales_gp_op_fcost(F_MF_Policy_df ,'F','MF')
            #print(F_MF_Policy_df)

            #Calculate Quarterly Figures and Change all the namings with a total infornt 
            F_MF_Quarter_Figures_df=calculate_quartery_figures(F_MF_Policy_df,'F','MF')

            #Calculate the volume and SKU Level GP Margin and OP Margin 
            F_MF_Final_df =  F_MF_Policy_df.merge(F_MF_Quarter_Figures_df, left_on='Quarter', right_on='Quarter', how='left')
            F_MF_Final_df=calculate_volume_gpm_opm(F_MF_Final_df ,'F','MF')

            #F_MF_Final_df.to_csv('MF_final_F.csv')
            F_MF_Final_df.to_excel(writer,
                            sheet_name='MF_Forecast_Information')

            #################################################################################
            #For actual 

            A_MF_Policy_df =  A_MF_df.merge(SKU_list, left_on='Item', right_on='SKU', how='left')
            #print(A_DS_Policy_df)
            #
            A_MF_Policy_df = calculate_sales_gp_op_fcost(A_MF_Policy_df ,'A','MF')

            A_MF_Quarter_Figures_df=calculate_quartery_figures(A_MF_Policy_df,'A','MF')

            #Until here is the same for forecast and actual #Can summarise into one function 
            #Only for the concatenating quarter part is only for actual 

            #print(A_MF_Quarter_Figures_df['BU_A_MF_FullCost_Total'])

            A_MF_Final_df=calculate_YTD(A_MF_Quarter_Figures_df,'A',"MF")

            #A_MF_Final_df.to_csv('test.csv')
            A_MF_Final_df.to_excel(writer,
                            sheet_name='MF_YTD_Information')

            #######################################################################################################################
            # #Forecast Preparation
            # #Joining Forecast and Actual 
            sorted_df=create_forecast_prep_df(F_MF_Final_df,A_MF_Final_df,'MF')
            writer.close()


            st.write("Data calculatedd...")
            st.dataframe(sorted_df)

            st.subheader('Downloads:')

            #file_path='data/Output.xlsx'
            file_path = "Data\\Output.xlsx"
            with open(file_path, 'rb') as my_file:
                st.download_button(label = '📥 Download Current Result', data = my_file, file_name = 'filename.xlsx', mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            

    else:
        st.markdown('Please go to the previous tab to upload a file first')



if selected == "Machine learning for fun":
    st.title('Simple ML profit prediction model')
    st.subheader('Enter the data below to predict the gross profit of an SKU. This simple ML model is trained using the IPL_data')
    
    qty_invoiced = st.slider('Quantity invoiced', 0, 10000, 500)
    price = st.number_input('Pkease enter the price',step=0.0001)
    # no. of bedrooms in the house
    extended_price = st.number_input('Extended Price',  step=0.0001)
    ext_price_usd = st.number_input('Ext Price USD', step=0.0001)
    custom_total_usd = st.number_input('Custom Total USD', step=0.0001)
    # how old is the house? (age)
    unit_cost = st.number_input('unit cost?',step=0.0001)
    ext_cost = st.number_input('ext cost?', step=0.0001)
     
    if st.button('Predict Gross Profit'):
        cost = predict(np.array([[qty_invoiced, price, extended_price, ext_price_usd,custom_total_usd,unit_cost,ext_cost]]))
        st.text(cost[0])
    #data = pd.read_excel('data/IPL_Data.xlsx')
#['Qty Invoiced', 'Price','Extended Price', 'Ext Price USD', 'Custom Total USD', 'Unit Cost', 'Ext Cost']
