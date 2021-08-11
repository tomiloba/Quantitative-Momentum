import pandas as pd
from scipy import stats
import math
import numpy as np
import xlsxwriter
import requests

#Import list of stocks
stocks = pd.read_csv('sp_500_stocks.csv')
#print(stocks)

from secrets import IEX_CLOUD_API_TOKEN
symbol ='AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/stats/?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()
#print(data)

#Parsing API Call
#USING BATCH API CALLS TO IMPROVE PERFOMANCE
def  chunks(lst, n):  #function to chunk list in seperate list of 100
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

#splits into lists of 100
symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = [] # empty list symbol string is a ist of string where each is a comma seperated string of all stocks in object(symbol_groups)
#print(symbol_groups)

#loop through every panda series within the list and executes batch api call and  for every stock in list append info for every stock in list to pandas dataframe
for i in range(0, len(symbol_groups)):
#   print(i)
#   print(symbol_groups[i])
    symbol_strings.append(','.join(symbol_groups[i]))
 #   print(symbol_strings[i])

#yearly_change= data['year1ChangePercent']
#print(yearly_change)

#BUILDING DATAFRAME

my_columns= ['Ticker','Price','1-Year Price Return', 'Number of Shares to Buy']

final_dataframe = pd.DataFrame(columns=my_columns)
#print(final_dataframe)

for symbol_string in symbol_strings:
    batch_api_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_url).json()
    #print(data)

    for symbol in symbol_string.split(','):

        final_dataframe= final_dataframe.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['quote']['latestPrice'],
                    data[symbol]['stats']['year1ChangePercent'],
                    'N/A'
                ],
                    index = my_columns),
                ignore_index= True
            )
    #print(final_dataframe)

#REMOVING LOW MOMENTUM STOCKS

#using panda libaries sort values method to sort the data in terms of yearly price returns
final_dataframe.sort_values('1-Year Price Return', ascending= False, inplace= True)
#inplace = True modify the sorted dataframe

#modify dataframe to only have first 50 rows
final_dataframe= final_dataframe[:30]

#reset index
final_dataframe.reset_index(inplace=True)
#print(final_dataframe)


#CALCULATING NUMBER OF SHARES TO BUY

def portfolio_input():
    global portfolio_size
    portfolio_size= input('Enter the size of your portfolio:')

    try:
        float(portfolio_size)
    except ValueError:

        print("This is not a number! \n Please try again:")
        portfolio_size = input('Enter the size of your portfolio:')

#portfolio_input()
#print(portfolio_size)

#position_size= float(portfolio_size) / len(final_dataframe.index)

#for i in range(0, len(final_dataframe.index)):
 #   final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / final_dataframe.loc[i, 'Price'])

#print(final_dataframe)

#REMOVING LOW MOMENTUM STOCKS(HIGH QUALITY MOMENTUM)

#Building High quality momentum dataframe
hqm_columns= ['Ticker',
              'Price',
              '1-Year Price Return',
              '1-Year Return Percentile',
              '6-Month Price Return',
              '6-Month Return Percentile',
              '3-Month Price Return',
              '3-Month Return Percentile',
              '1-Month Price Return',
              '1-Month Return Percentile',
              'Number of Shares to Buy',
              'High Quality Momentum Score'
              ]

#Creating a blank dataframe and adding data one by one to the dataframe

hqm_dataframe= pd.DataFrame(columns = hqm_columns)
#example of a symbol_string variable = 'AAPL'
for symbol_string in symbol_strings[:200]:
   # print(symbol_strings)
    batch_api_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data= requests.get(batch_api_url).json()
   # print(data)


    for symbol in symbol_string.split(','):
        hqm_dataframe= hqm_dataframe.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]['quote']['latestPrice'], #stock price
                    data[symbol]['stats']['year1ChangePercent'], #one year price return
                    'N/A',
                    data[symbol]['stats']['month6ChangePercent'], #six month price rerurn
                    'N/A',
                    data[symbol]['stats']['month3ChangePercent'],#three month price retrun
                    'N/A',
                    data[symbol]['stats']['month1ChangePercent'],#one month price return
                    'N/A',
                    'N/A',
                    'N/A'
                ],
                index= hqm_columns),
            ignore_index= True
        )
#print(hqm_dataframe)


#CALCULATING MOMENTUM PERCENTILE

time_periods = [
    '1-Year',
    '6-Month',
    '3-Month',
    '1-Month'
]

#loop calculate percentile scores for every percentile column

for row in hqm_dataframe.index:
    #print(row)
    for time_period in time_periods:
        #print(time_period)

        percentile_col = f'{time_period} Return Percentile' #percentile scores
        change_col = f'{time_period} Price Return' #price return
        hqm_dataframe[change_col] = hqm_dataframe[change_col].astype(float) #converts change_col data type to float

        #print(type(change_col))
        #print(type(percentile_col))
        #print(percentile_col)
        #print(tester)
        #print(hqm_dataframe[change_col])
        hqm_dataframe.loc[row, percentile_col ] = stats.percentileofscore(hqm_dataframe[change_col], hqm_dataframe.loc[row,change_col])/100

#CALCULATING THE HQM SCORE

#hqm score is the mean of the 4 momentum percentile scores
from statistics import mean

for row in hqm_dataframe.index:
    momentum_percentiles = []

    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe.loc[row, f'{time_period} Return Percentile'])
    #print(momentum_percentiles)
    hqm_dataframe.loc[row,'High Quality Momentum Score'] = mean(momentum_percentiles)

#SELECTING 100 STOCKS WITH THE HIGHEST MOMENTUM SCORES
hqm_dataframe.sort_values('High Quality Momentum Score', ascending= False, inplace= True)
#inplace = True modify the sorted dataframe

#modify dataframe to only have first 100 rows
hqm_dataframe= hqm_dataframe[:100]

#reset index
hqm_dataframe.reset_index(inplace=True, drop=True)

#CALCULATING NUMBER OF SHARES TO BUY

portfolio_input()

position_size= float(portfolio_size) / len(hqm_dataframe.index)

for i in range(0, len(hqm_dataframe.index)):
    hqm_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / hqm_dataframe.loc[i, 'Price'])



print(hqm_dataframe)


#FORMATTING EXCEL OUTPUT
#initialize xlsx object

writer = pd.ExcelWriter('Highest Momentum Trades.xlsx', engine= 'xlsxwriter') #@param(file name, engine)
hqm_dataframe.to_excel(writer, "Highest Momentum Trades", index=False) #@param('writer', Tab Name, index=False)

#store HTML hex codes for colors selected
background_color='#0a0a23'
font_color='ffffff'

string_format = writer.book.add_format(
    {
        'font_color': font_color,
        'bg_color': background_color,
        'border': 1

    }
)
dollar_format = writer.book.add_format(
    {
        'num_format': '$0.00',
        'font_color': font_color,
        'bg_color': background_color,
        'border': 1

    }
)

percent_format = writer.book.add_format(
    {
        'num_format': '%0.00',
        'font_color': font_color,
        'bg_color': background_color,
        'border': 1

    }
)

integer_format = writer.book.add_format(
    {
        'num_format': '0',
        'font_color': font_color,
        'bg_color': background_color,
        'border': 1

    }
)


column_formats = {
    'A':['Ticker', string_format],
    'B':['Price', dollar_format],
    'C':['1-Year Price Return',percent_format],
    'D': ['1-Year Return Percentile', percent_format],
    'E': ['6-Month Price Return', percent_format],
    'F': ['6-Month Return Percentile', percent_format],
    'G':['3-Month Price Return',percent_format],
    'H': ['3-Month Return Percentile', percent_format],
    'I': ['1-Month Price Return', percent_format],
    'J': ['3-Month Return Percentile', percent_format],
    'K':['Number of Shares to Buy', integer_format],
    'L':['High Quality Momentum Score', percent_format]

}
for column in column_formats.keys():
    writer.sheets['Highest Momentum Trades'].set_column(f'{column}:{column}',20,column_formats[column][1])
    writer.sheets['Highest Momentum Trades'].write(f'{column}1', column_formats[column][0],string_format)
writer.save()
