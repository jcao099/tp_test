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

#switch_page("New page name")
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



if selected == "Upload and view Data":
    st.title('TP SKU calculation engine 📈')
    
    st.subheader('Please upload the Excel file')
    uploaded_file = st.file_uploader("Choose a XLSX file with column names of 'Item', 'Quarter', 'COGS', 'OP Expemses'. If you don't have a file, you can click the button to use the mock data"
        ,type='xlsx')

    use_mock = st.button("Use mock data")

    if uploaded_file:
        #st.markdown('---')
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.session_state.df = df

        # clean_button = st.button("Click here to clean the data!")
        # #st.write(clean_button)
        # if clean_button:
        #     st.write("Data cleaned...")
        #     st.dataframe(df)
        #     st.session_state.clean = True

    if use_mock:
        df = pd.read_excel('data/Cleaned_Data_for_Engine.xlsx')
        st.session_state.df = df
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
        st.markdown('Your uploaded file')
        st.dataframe(df)
        method = st.selectbox(
        "How would you like to be calculated?",
        ("TopDown Approach", "Bottom_up approach"),)
        calculate_button = st.button("Click here to caltulate!")
        #st.write(clean_button)
        if calculate_button:
            st.write("Data calculatedd...")
            st.subheader('Downloads:')
            generate_excel_download_link(df)

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
