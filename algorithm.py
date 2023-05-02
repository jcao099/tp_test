import pandas as pd

def calculate_forecast(df,type='OM',target=0.03):
    ytd_operating_margin=df['BU_A_DS_OP_Margin_YTD'][0]
    operating_profit_ytd=df['BU_A_DS_OP_YTD'][0]
    sales_ytd=df['BU_A_DS_Sales_YTD'][0]
    gross_margin_ytd=df['BU_A_DS_GP_YTD'][0]/df['BU_A_DS_Sales_YTD'][0]
    gross_profit_ytd=df['BU_A_DS_GP_YTD'][0]

    if type=='GM':
        metric=gross_margin_ytd
        margin_type='GP'

    elif type=='OM':
        metric=ytd_operating_margin
        margin_type='OP'

    else:
        return 'Invalid Type'

    new_df = pd.DataFrame(columns=['BU_DS_SKU',
                                'BU_DS_Quarter',
                                'BU_DS_Budget_Sales',
                                'BU_DS_Budget_COGS',
                                'BU_DS_New_COGS',
                                'BU_DS_GP',
                                'BU_DS_GP_Margin',
                                'BU_DS_New_'+margin_type+'_Margin',
                                'BU_DS_Adjusted Percentage',
                                'BU_DS_Adjustment Status'])

    if metric>target:
        sign='positive'
        
    else:
        sign='negative'
        
    if sign=='negative':
        #Trying to increase
        #So attemp the smallest increase first 
        #If the smallest increase fulfil the requirement, break from the loop
        start=1
        end=6
        step=1

    else:
        start=5
        end=0
        step=-1

    #print(metric)
    if metric!=target:
        for i in range(len(df)):
            
        #     if (i==0 and ytd_distributor_margin>0.03) or (len(new_df)>0 and new_df.iloc[len(new_df)-1]['DT_New_Distributor_Margin']>0.03):

        #         sign='positive'

        #     else:

        #         sign='negative'

            if len(new_df)>0:
                check_val=new_df.iloc[len(new_df)-1]['BU_DS_New_'+margin_type+'_Margin']
                
                if (sign=='positive' and check_val<=target) or (sign=='negative' and check_val>=target):
                    #print('Cannot adjust further')
                    break

            budget_cogs = df.iloc[i]['COGS']
            budget_sales= df.iloc[i]['BU_F_DS_Sales']
            forecast_total_cogs=df.iloc[i]['COGS_Total']
            running_total_new_cogs = sum(new_df['BU_DS_New_COGS'])
            running_total_budget_cogs = sum(new_df['BU_DS_Budget_COGS'])
            forecast_total_sales =df.iloc[i]['BU_F_DS_Sales_Total']
            forecast_total_op_expenses=df.iloc[i]['OP_expenses_Total']
            SKU=df.iloc[i]['SKU']
            Quarter=df.iloc[i]['Quarter']

            #prev=False 
            #for j in range(5,0,-1):
            for j in range(start,end,step):

                if sign=='positive':
                    change=1+j/100

                else:
                    change=1-j/100

                #print(change)
                #print(j//100)
                new_cogs = budget_cogs*change
                new_cogs_all=forecast_total_cogs + running_total_new_cogs +new_cogs-running_total_budget_cogs-budget_cogs
                new_gross_profit = budget_sales - new_cogs
                new_gross_margin = new_gross_profit / budget_sales
                # print('new GM')
                # print(new_gross_margin)
                new_gross_profit_all= forecast_total_sales - new_cogs_all 
                #new_gross_margin_all=new_gross_profit_all/forecast_total_sales
                new_operating_profit =new_gross_profit_all-forecast_total_op_expenses
                
                if type=='OM':
                    operating_margin=(new_operating_profit+operating_profit_ytd)/(forecast_total_sales+sales_ytd)
                    metric=operating_margin
                    #new_gross_margin_all=new_gross_profit_all/forecast_total_sales
                    if operating_margin>target and new_gross_margin>0:
                        break

                elif type=='GM':
                    #including YTD 
                    new_gross_margin_all=(new_gross_profit_all+gross_profit_ytd) / (forecast_total_sales+sales_ytd)
                    metric=new_gross_margin_all
                    if new_gross_margin_all>target:
                        break 

            if type=='OM':
                if operating_margin>target and new_gross_margin>0:
                    adjustments='adjust'
                else:
                    adjustments='dont adjust'

            elif type=='GM':
                if new_gross_margin_all>target:
                    adjustments='adjust'
                else:
                    adjustments='dont adjust'


            ##Comment out this line to show everything
            if adjustments=='dont adjust':
                #break
                #print('here')
                continue


            #Append to new df  
            # initialize data of lists.
            #print(new_gross_margin)
            data=[{'BU_DS_SKU':SKU,
                'BU_DS_Quarter':Quarter,
                'BU_DS_Budget_Sales':budget_sales,
                'BU_DS_Budget_COGS':budget_cogs,
                'BU_DS_New_COGS':new_cogs,
                'BU_DS_GP': new_gross_profit,
                'BU_DS_GP_Margin': new_gross_margin,
                'BU_DS_New_'+margin_type+'_Margin':metric,#operating_margin,#Gross margin all 
                'BU_DS_Adjusted Percentage':change -1,
                'BU_DS_Adjustment Status':adjustments}]
            # Create DataFrame
            temp_df = pd.DataFrame(data)
        #     print(i)
        #     print(temp_df)
            new_df = new_df.append(temp_df)
            #print(new_df)

            #use the value calculated above 
            if type=='OM':
                if operating_margin==target:
                    break

            elif type=='GM':
                if new_gross_margin_all==target:
                    break 

    new_df = new_df.reset_index(drop=True)
    new_df['index'] = new_df.index
    
    return new_df 