#Creating functions 
import pandas as pd

def calculate_sales_gp_op_fcost(df,category,side):
    """
    category refers to F or A
    side refers to Distributor or Manufacturer 
    For MF, we are calculating the FullCost as well 
    """
    name_str=category+'_'+side

    df['BU_'+name_str+'_Sales']=df['Price']*df['Quantity']
    df['BU_'+name_str+'_GP']=df['BU_'+name_str+'_Sales']-df['COGS']
    df['BU_'+name_str+'_OP']=df['BU_'+name_str+'_GP']-df['OP_expenses']

    if side=='MF':
         df['BU_'+name_str+'_FullCost']=df['OP_expenses']+df['COGS']

    return df 

def calculate_quartery_figures(df,category,side):
    """
    category refers to F or A
    side refers to Distributor or Manufacturer 

    """
    name_str=category+'_'+side

    aggs={
        'Quantity':lambda x: sum(x),
        'BU_'+name_str+'_Sales':lambda x: sum(x),
        'COGS':lambda x: sum(x),
        'BU_'+name_str+'_GP': lambda x: sum(x),
        'OP_expenses':lambda x: sum(x),
        'BU_'+name_str+'_OP':lambda x: sum(x),
        'BU_'+name_str+'_FullCost':lambda x: sum(x),
        }

    #The following line make sure that the data only aggregates if the column exist
    #https://stackoverflow.com/questions/46937399/pandas-groupby-and-agg-ignore-errors
    df=df.groupby(['Quarter']).agg({k:v for k,v in aggs.items() if k in df}).reset_index()

    column_names={'Quantity':'Quantity_Total',
                'BU_'+name_str+'_Sales':'BU_'+name_str+'_Sales'+'_Total',
                'COGS':'COGS_Total',
                'BU_'+name_str+'_GP': 'BU_'+name_str+'_GP'+'_Total',
                'OP_expenses':'OP_expenses_Total',
                'BU_'+name_str+'_OP':'BU_'+name_str+'_OP'+'_Total',
                'BU_'+name_str+'_FullCost': 'BU_'+name_str+'_FullCost_Total'
                }

    df=df.rename(columns={k:v for k,v in column_names.items() if k in df})

    df['BU_'+name_str+'_GP_Margin_Quarter']=(df['BU_'+name_str+'_Sales'+'_Total']-df['COGS_Total'])/df['BU_'+name_str+'_Sales'+'_Total']
    df['BU_'+name_str+'_OP_Margin_Quarter']=df['BU_'+name_str+'_OP'+'_Total']/df['BU_'+name_str+'_Sales'+'_Total']

    if side=='MF':
        df['BU_'+name_str+'_FCMU_Quarter']=df['BU_'+name_str+'_OP'+'_Total']/df['BU_'+name_str+'_FullCost'+'_Total']

    #df.to_csv('quarter.csv')
    return df 


def calculate_volume_gpm_opm(df,category,side):
    """
    category refers to F or A
    side refers to Distributor or Manufacturer 

    """
    name_str=category+'_'+side

    df['BU_'+name_str+'_Volume']=(df['COGS']/df['COGS_Total']*100).apply(lambda x : round(x,0)) if side=='DS' else (df['BU_'+name_str+'_Sales']/df['BU_'+name_str+'_Sales'+'_Total']*100).apply(lambda x : round(x,0))
    df['BU_'+name_str+'_GP_Margin']=(df['BU_'+name_str+'_Sales']-df['COGS'])/df['BU_'+name_str+'_Sales']
    df['BU_'+name_str+'_OP_Margin']=df['BU_'+name_str+'_OP']/df['BU_'+name_str+'_Sales']

    if side=='MF':
        df['BU_'+name_str+'_FCMU']=df['BU_'+name_str+'_OP']/(df['COGS']+df['OP_expenses'])

    df=df.drop(columns=['Item'])
    return df 


#For actual 
def calculate_YTD(df,category,side):
    """
    category refers to F or A
    side refers to Distributor or Manufacturer 

    """
    #Using a dummy col for group by
    name_str=category+'_'+side
    df['dummy_col']=0
    
    #https://stackoverflow.com/questions/68091853/python-cannot-perform-both-aggregation-and-transformation-operations-simultaneo
    
    aggs={
        'Quantity_Total':lambda x: sum(x),
        'BU_'+name_str+'_Sales'+'_Total':lambda x: sum(x),
        'COGS_Total':lambda x: sum(x),
        'BU_'+name_str+'_GP'+'_Total': lambda x: sum(x),
        'OP_expenses_Total':lambda x: sum(x),
        'BU_'+name_str+'_OP'+'_Total':lambda x: sum(x),
        "Quarter":lambda x: "".join(x),
        'BU_'+name_str+'_FullCost_Total':lambda x: sum(x),
        }
    Final_df=df.groupby(['dummy_col']).agg({k:v for k,v in aggs.items() if k in df}).reset_index()
    
    
    column_names={'Quantity_Total':'Quantity_YTD',
                    'BU_'+name_str+'_Sales'+'_Total':'BU_'+name_str+'_Sales'+'_YTD',
                    'COGS_Total':'COGS_YTD',
                    'BU_'+name_str+'_GP'+'_Total':'BU_'+name_str+'_GP'+'_YTD',
                    'OP_expenses_Total':'OP_expenses_YTD',
                    'BU_'+name_str+'_OP'+'_Total':'BU_'+name_str+'_OP'+'_YTD',
                    "Quarter":'Concat_Quarter', 
                    'BU_'+name_str+'_FullCost_Total': 'BU_'+name_str+'_FullCost_YTD'
    }
                                                

    Final_df=Final_df.rename(columns={k:v for k,v in column_names.items() if k in df})

    Final_df=Final_df.drop(columns=['dummy_col'])
    #print(Final_df)

    #BU_A_DS_GP_Margin_Quarter and BU_A_DS_OP_Margin_Quarter not needed after aggregations 
    Final_df['BU_'+name_str+'_GP_Margin_YTD']=(Final_df['BU_'+name_str+'_Sales'+'_YTD']-Final_df['COGS_YTD'])/Final_df['BU_'+name_str+'_Sales'+'_YTD']
    Final_df['BU_'+name_str+'_OP_Margin_YTD']=Final_df['BU_'+name_str+'_OP'+'_YTD']/Final_df['BU_'+name_str+'_Sales'+'_YTD']
    
    if side=='MF':
        Final_df['BU_'+name_str+'_FCMU_YTD']=Final_df['BU_'+name_str+'_OP'+'_YTD']/Final_df['BU_'+name_str+'_FullCost_YTD']
    
    Final_df['Forecast_Quarter']=Final_df['Concat_Quarter'].apply(lambda x: "Q"+str(int(x[-1])+1))

    return Final_df

def create_forecast_prep_df(forecast_df,actual_df,side):
    """
    side refers to Distributor or Manufacturer 
    """
    
    Final_df=forecast_df.merge(actual_df, left_on='Quarter', right_on='Forecast_Quarter', how='inner')
    # Final_df=Final_df.drop(columns=['Item'])
    sorted_df = Final_df.sort_values(by=['BU_F_'+side+'_Volume'], ascending=False)

    return sorted_df 


