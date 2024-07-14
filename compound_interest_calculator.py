import streamlit as st
import pandas as pd
import altair as alt
import time



### Setting page configs + header
st.set_page_config(page_title="Zinseszinsrechner", layout="centered", page_icon=":chart_with_upwards_trend:")
st.subheader(':blue[Zinseszinsrechner]', divider='blue')

st.info("Die Steuern werden nach der Verzinsungsart abgeliefert", icon="ℹ️")


### CSS for results
st.markdown("""
    <style>
   
    .custom-number {
        font-family: 'SF Pro Display', sans-serif;
        font-size: 16px;
        text-align: right;
        font-weight: 500;
        letter-spacing: 0.02em; }

    </style>
    """, unsafe_allow_html=True)
def add_space(height):
    st.markdown(f"<div style='height: {height}px;'></div>", unsafe_allow_html=True)


### 1.row with 2 inputs
row1_col1, row1_col2 = st.columns(2)
money_input = row1_col1.number_input("Kapital (in €)", min_value=0.00)
interest_rate = row1_col2.number_input("Zinsniveau p.a. (in %)", min_value=0.00)


### 2.row with 2 inputs
row2_col1, row2_col2 = st.columns(2)
time_period = row2_col1.number_input("Zeitraum (in Jahren)", min_value=0)
interest_type = row2_col2.selectbox("Verzinsungsart", ["jährlich", "quartalsweise", "monatlich"])


### 3.row with 2 inputs
row3_col1, row3_col2 = st.columns(2)
monthly_rate = row3_col1.number_input("monatliche Rate", min_value=0.00)
tax_rate = row3_col2.number_input("KESt (in %)", min_value=0.00)


### Toggling element for tax only once
on_tax = st.toggle("Steuer wird nur einmal am Ende fällig")

### Adding space
add_space(35)

### Adding subheader for results
st.subheader(':blue[Ergebnisse]', divider='blue')


### Define variables for calculation
if interest_type == "jährlich":
    k = 1
    multiplier_for_ebt = 12
    ebt_inpayments_graphic = 0
    
elif interest_type == "quartalsweise":
    k = 4
    multiplier_for_ebt = 3
    interest_rate_quarterly = ((1 + (interest_rate / 100)) ** (1 / k)) - 1
    ebt_inpayments_graphic = 0
    
elif interest_type == "monatlich":
    k = 12
    multiplier_for_ebt = 1
    interest_rate_monthly = ((1 + (interest_rate / 100)) ** (1 / k)) - 1
    ebt_inpayments_graphic = 0



################################ äquivalenter Zinssatz ################################


### Calculating total capital
def total_capital(money_input,interest_rate,time_period,monthly_rate,k):
    
    if monthly_rate == 0.00:
        ebt = (money_input * ((1 + (interest_rate / 100)) ** (1 / k)) ** (time_period * k))
    else:
        ebt = (money_input * ((1 + (interest_rate / 100)) ** (1 / k)) ** (time_period * k)) + (monthly_rate * multiplier_for_ebt) * (((1 + (interest_rate / 100)) ** (1 / k)) ** (int(time_period) * k) - 1) / (((1 + (interest_rate / 100)) ** (1 / k)) - 1)
    
    return ebt
call_gk_funtion = total_capital(money_input,interest_rate,time_period,monthly_rate,k)

def total_capital_for_graphic(money_input,interest_rate,time_period,monthly_rate,k, ebt_inpayments_graphic):
    
    if monthly_rate == 0.00:
        
        ebt_total_graphic_list = []
        ebt_interest_graphic_list =[]
        ebt_starting_capital_list =[]
        
        for i in range (1, int(time_period + 1)):
            ebt_total_graphic = (money_input * ((1 + (interest_rate / 100)) ** (1 / k)) ** (i * k))
            ebt_interest_graphic = ebt_total_graphic - money_input
            ebt_inpayments_graphic = money_input
            
            ebt_starting_capital_list.append(ebt_inpayments_graphic)
            ebt_interest_graphic_list.append(ebt_interest_graphic)
            ebt_total_graphic_list.append(ebt_total_graphic)
           
    else:
        
        ebt_total_graphic_list = []
        ebt_interest_graphic_list =[]
        ebt_starting_capital_list =[]
        
        for i in range (1, int(time_period + 1)):
            ebt_total_graphic = (money_input * ((1 + (interest_rate / 100)) ** (1 / k)) ** (i * k)) + (monthly_rate * multiplier_for_ebt) * (((1 + (interest_rate / 100)) ** (1 / k)) ** (i * k) - 1) / (((1 + (interest_rate / 100)) ** (1 / k)) - 1)
            ebt_interest_graphic = ebt_total_graphic - money_input - (monthly_rate * 12 * i)
            ebt_inpayments_graphic = money_input + (monthly_rate * 12 * i)
            
            ebt_starting_capital_list.append(ebt_inpayments_graphic)
            ebt_interest_graphic_list.append(ebt_interest_graphic)
            ebt_total_graphic_list.append(ebt_total_graphic)
            
    
    return ebt_starting_capital_list, ebt_interest_graphic_list, ebt_total_graphic_list


### Calculating all metrics (yearly)
def calculator_yearly(money_input,interest_rate,time_period,tax_rate):
    
    kest_yearly = []
    total_amount_yearly = []
    starting_capital = money_input

    for jahre in range(1, int(time_period) + 1):
        
        interest_deduction = money_input * (interest_rate / 100) * (tax_rate / 100)
        kest_yearly.append(interest_deduction)
        
        
        total_amount = (money_input * (1 + (interest_rate / 100))) - (interest_deduction)
        money_input = total_amount
        total_amount_yearly.append(money_input)

    
    sum_gk = call_gk_funtion
    sum_ebt = (total_amount_yearly[-1] - starting_capital + sum(kest_yearly)) if total_amount_yearly else 0
    sum_kest = sum(kest_yearly)
    sum_eat = (total_amount_yearly[-1] - starting_capital) if total_amount_yearly else 0
   
    
    return sum_gk, sum_ebt, sum_kest, sum_eat

def calculator_yearly_extra(money_input,interest_rate,time_period,tax_rate,monthly_rate):
    kest_yearly = []
    total_amount_yearly = []
    starting_capital = money_input  

    for jahre in range(1, int(time_period) + 1):
        
        interest_deduction = money_input * (interest_rate / 100) * (tax_rate / 100)
        kest_yearly.append(interest_deduction)
        
        
        total_amount = (money_input * (1 + (interest_rate / 100))) - (interest_deduction)
        money_input = total_amount + monthly_rate * 12
        total_amount_yearly.append(money_input)


    sum_gk = call_gk_funtion 
    sum_ebt = (total_amount_yearly[-1] - (starting_capital + monthly_rate * 12 * int(time_period)) + sum(kest_yearly)) if total_amount_yearly else 0
    sum_kest = sum(kest_yearly)
    sum_eat = (total_amount_yearly[-1] - (starting_capital + monthly_rate * 12 * int(time_period))) if total_amount_yearly else 0
    
    
    return sum_gk, sum_ebt, sum_kest, sum_eat



### Calculating all metrics (quarterly)
def calculator_quarterly(money_input, time_period, tax_rate, interest_rate_quarterly):
    
    kest_quarterly = []
    total_amount_quarterly = []
    starting_capital = money_input

    for jahre in range(1, int(time_period) + 1):
        for quartale in range(1, int(k)+1):
            
            interest_deduction = money_input * interest_rate_quarterly * (tax_rate / 100)
            kest_quarterly.append(interest_deduction)
            
            
            total_amount = (money_input * (1 + interest_rate_quarterly)) - (interest_deduction)
            money_input = total_amount
            total_amount_quarterly.append(money_input)
    
    
    sum_gk = call_gk_funtion
    sum_ebt = (total_amount_quarterly[-1] - starting_capital + sum(kest_quarterly)) if total_amount_quarterly else 0
    sum_kest = sum(kest_quarterly)
    sum_eat = (total_amount_quarterly[-1] - starting_capital) if total_amount_quarterly else 0
    
    
    return sum_gk, sum_ebt, sum_kest, sum_eat

def calculator_quarterly_extra(money_input, time_period, tax_rate, interest_rate_quarterly, monthly_rate):
    
    kest_quarterly = []
    total_amount_quarterly = []
    starting_capital = money_input

    for jahre in range(1, int(time_period) + 1):
        for quartale in range(1, int(k)+1):
            
            interest_deduction = money_input * interest_rate_quarterly * (tax_rate / 100)
            kest_quarterly.append(interest_deduction)
            
            
            total_amount = (money_input * (1 + interest_rate_quarterly)) - (interest_deduction)
            money_input = total_amount + monthly_rate * 3
            total_amount_quarterly.append(money_input)
    
    
    sum_gk = call_gk_funtion 
    sum_ebt = (total_amount_quarterly[-1] - (starting_capital + monthly_rate * 12 * int(time_period)) + sum(kest_quarterly)) if total_amount_quarterly else 0
    sum_kest = sum(kest_quarterly)
    sum_eat = (total_amount_quarterly[-1] - (starting_capital + monthly_rate * 12 * int(time_period))) if total_amount_quarterly else 0
    
    
    return sum_gk, sum_ebt, sum_kest, sum_eat



### Calculating all metrics (monthly)
def calculator_monthly(money_input,time_period,tax_rate,interest_rate_monthly):
       
    kest_monthly = []
    total_amount_monthly = []
    starting_capital = money_input

    for jahre in range(1, int(time_period) + 1):
        for monate in range(1, int(k)+1):
            
            interest_deduction = money_input * interest_rate_monthly * (tax_rate / 100)
            kest_monthly.append(interest_deduction)
            
            
            total_amount = (money_input * (1 + interest_rate_monthly)) - (interest_deduction)
            money_input = total_amount
            total_amount_monthly.append(money_input)


    sum_gk = call_gk_funtion
    sum_ebt = (total_amount_monthly[-1] - starting_capital + sum(kest_monthly)) if total_amount_monthly else 0
    sum_kest = sum(kest_monthly)
    sum_eat = (total_amount_monthly[-1] - starting_capital) if total_amount_monthly else 0
   
    
    return sum_gk, sum_ebt, sum_kest, sum_eat

def calculator_monthly_extra(money_input,time_period,tax_rate,interest_rate_monthly, monthly_rate):
    
    kest_monthly = []
    total_amount_monthly = []
    starting_capital = money_input

    for jahre in range(1, int(time_period) + 1):
        for monate in range(1, int(k)+1):
            
            interest_deduction = money_input * interest_rate_monthly * (tax_rate / 100)
            kest_monthly.append(interest_deduction)
            
            
            total_amount = (money_input * (1 + interest_rate_monthly)) - (interest_deduction)
            money_input = total_amount + monthly_rate
            total_amount_monthly.append(money_input)


    sum_gk = call_gk_funtion 
    sum_ebt = (total_amount_monthly[-1] - (starting_capital + monthly_rate * 12 * int(time_period)) + sum(kest_monthly)) if total_amount_monthly else 0
    sum_kest = sum(kest_monthly)
    sum_eat = (total_amount_monthly[-1] - (starting_capital + monthly_rate * 12 * int(time_period))) if total_amount_monthly else 0
    
    
    return sum_gk, sum_ebt, sum_kest, sum_eat


### Calling function + Displaying results
if monthly_rate == 0.00 and interest_type == "jährlich" and not on_tax:
    results_yearly = calculator_yearly(money_input,interest_rate,time_period, tax_rate)
    

    ### Containers for each row
    row1 = st.container()
    row2 = st.container()
    row3 = st.container()
    row4 = st.container()
    
    
    ### Displaying each row
    with row1:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gesamtkapital")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_yearly[0]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row2:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn vor Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_yearly[1]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row3:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("###### KESt")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_yearly[2]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row4:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn nach Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_yearly[3]:,.0f}€</div>", unsafe_allow_html=True)
elif monthly_rate > 0.00 and interest_type == "jährlich" and not on_tax:
    results_yearly_extra = calculator_yearly_extra(money_input,interest_rate,time_period,tax_rate,monthly_rate)
    
    
    ### Containers for each row
    row1 = st.container()
    row2 = st.container()
    row3 = st.container()
    row4 = st.container()
    
    
    ### Displaying each row
    with row1:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gesamtkapital")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_yearly_extra[0]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row2:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn vor Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_yearly_extra[1]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row3:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("###### KESt")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_yearly_extra[2]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row4:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn nach Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_yearly_extra[3]:,.0f}€</div>", unsafe_allow_html=True)


### Calling function + Displaying results
if monthly_rate == 0.00 and interest_type == "quartalsweise" and not on_tax:
    results_quarterly = calculator_quarterly(money_input, time_period, tax_rate, interest_rate_quarterly)
       

    ### Containers for each row
    row1 = st.container()
    row2 = st.container()
    row3 = st.container()
    row4 = st.container()
    
    
    ### Displaying each row
    with row1:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gesamtkapital")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_quarterly[0]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row2:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn vor Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_quarterly[1]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row3:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("###### KESt")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_quarterly[2]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row4:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn nach Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_quarterly[3]:,.0f}€</div>", unsafe_allow_html=True)
elif monthly_rate > 0.00 and interest_type == "quartalsweise" and not on_tax:
    results_quarterly_extra = calculator_quarterly_extra(money_input,time_period,tax_rate,interest_rate_quarterly,monthly_rate)
    

    ### Containers for each row
    row1 = st.container()
    row2 = st.container()
    row3 = st.container()
    row4 = st.container()
    
    
    ### Displaying each row
    with row1:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gesamtkapital")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_quarterly_extra[0]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row2:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn vor Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_quarterly_extra[1]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row3:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("###### KESt")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_quarterly_extra[2]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row4:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn nach Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_quarterly_extra[3]:,.0f}€</div>", unsafe_allow_html=True)


#### Calling function + Displaying results
if monthly_rate == 0.00 and interest_type == "monatlich" and not on_tax:
    results_monthly = calculator_monthly(money_input,time_period,tax_rate,interest_rate_monthly)
       
    
    ### Containers for each row
    row1 = st.container()
    row2 = st.container()
    row3 = st.container()
    row4 = st.container()
    
    
    ### Displaying each row
    with row1:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gesamtkapital")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_monthly[0]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row2:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn vor Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_monthly[1]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row3:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("###### KESt")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_monthly[2]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row4:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn nach Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_monthly[3]:,.0f}€</div>", unsafe_allow_html=True)
elif monthly_rate > 0.00 and interest_type == "monatlich" and not on_tax:
    results_monthly_extra = calculator_monthly_extra(money_input,time_period,tax_rate,interest_rate_monthly, monthly_rate)
    
    
    ### Containers for each row
    row1 = st.container()
    row2 = st.container()
    row3 = st.container()
    row4 = st.container()
    
    
    ### Displaying each row
    with row1:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gesamtkapital")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_monthly_extra[0]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row2:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn vor Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_monthly_extra[1]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row3:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("###### KESt")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_monthly_extra[2]:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row4:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn nach Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{results_monthly_extra[3]:,.0f}€</div>", unsafe_allow_html=True)





### Tax only calculated at the end of the time
if on_tax:
    only_tax_gk = call_gk_funtion
    only_tax_ebt = only_tax_gk - money_input - (monthly_rate * 12 * int(time_period))
    only_tax_kest = only_tax_ebt * (tax_rate/100)
    only_tax_eat = only_tax_ebt - only_tax_kest
    

    ### Containers for each row
    row1 = st.container()
    row2 = st.container()
    row3 = st.container()
    row4 = st.container()
    
    
    ### Displaying each row
    with row1:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gesamtkapital")
        with col2:
            st.markdown(f"<div class='custom-number'>{only_tax_gk:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row2:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn vor Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{only_tax_ebt:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row3:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("###### KESt")
        with col2:
            st.markdown(f"<div class='custom-number'>{only_tax_kest:,.0f}€</div>", unsafe_allow_html=True)

    add_space(6)

    with row4:
        col1, col2 = st.columns([3, 1])  
        with col1:
            st.write("###### Gewinn nach Steuern")
        with col2:
            st.markdown(f"<div class='custom-number'>{only_tax_eat:,.0f}€</div>", unsafe_allow_html=True)
    


################################ graphische Darstellung ################################


### Creating table as data source for chart
getting_data = total_capital_for_graphic(money_input, interest_rate, time_period, monthly_rate, k, ebt_inpayments_graphic)
years = list(range(1, 1 + int(time_period)))
data = {'Year': years,'Einzahlungen': getting_data[0], 'Zinsen':getting_data[1],'Kapital': getting_data[2]}
df = pd.DataFrame(data)


### DataFrame into another format
df_long = pd.melt(df, id_vars=['Year'], value_vars=['Zinsen', 'Einzahlungen'], var_name='Type', value_name='Amount')
df_long = pd.melt(df, id_vars=['Year'], value_vars=['Einzahlungen', 'Zinsen'], var_name='Category', value_name='Amount')
df_long['Category'] = pd.Categorical(df_long['Category'], categories=['Einzahlungen', 'Zinsen'], ordered=True)


### Creating the chart
stacked_chart = alt.Chart(df_long).mark_bar().encode(
    x=alt.X('Year:O', title='Jahre', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('sum(Amount):Q', title='Kapital'),
    color=alt.Color('Category:N',legend=alt.Legend(title="", symbolType="circle", values=["Zinsen", "Einzahlungen"])), 
    order=alt.Order('Category', sort='ascending'),
    tooltip=['Year', 'Category', alt.Tooltip('sum(Amount)', format='.0f', title='Amount')]
).properties(
    width=900,
    height=300,
)


### Toggle element to display the chart
on = st.toggle("Grafik anzeigen")
if on:
    with st.spinner("Mapping data..."):
        time.sleep(1)
    st.altair_chart(stacked_chart, use_container_width=True) 
else:
    pass