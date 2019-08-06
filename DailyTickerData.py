
# # https://www.alphavantage.co/documentation/?
# https://github.com/RomelTorres/alpha_vantage

from alpha_vantage.timeseries import TimeSeries
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from yahoo_earnings_calendar import YahooEarningsCalendar


ts = TimeSeries(key='YCZ9XRMG0CPPQTRG', output_format='pandas')
data, meta_data = ts.get_daily_adjusted(symbol='UAA')

data = data.rename(columns={'date': 'udate', '4. close': 'close'})
# print(data.head(110))

#Make the db in memory
conn = sqlite3.connect(':memory:')

data.to_sql('close_cur', conn)
data.to_sql('close_yst', conn)
data.to_sql('close_yst2', conn)

qry = '''
    SELECT dateof, ROUND((((close0)/close_before)-1)*100,2) as BMO_1day_per_change, ROUND((((close1)/close_before)-1)*100,2) as BMO_2day_per_change,
                   ROUND((((close1)/close0)-1)*100,2) as AMC_1day_per_change, ROUND((((close2)/close0)-1)*100,2) as AMC_2day_per_change
    FROM
            (SELECT
                date(date) as dateof,
                (SELECT COUNT()+1 FROM (
                    SELECT DISTINCT date FROM close_cur AS t WHERE date < close_cur.date)) as rank,
                close as close0
            FROM close_cur) cur
    LEFT JOIN
            (SELECT
                date(date) as dayafter1,
                (SELECT COUNT()+1 FROM (
                    SELECT DISTINCT date FROM close_cur AS t WHERE date < close_yst.date)) as rank,
                close as close1
            FROM close_yst) yst
    ON cur.rank = yst.rank-1
    LEFT JOIN 
            (SELECT
                date(date) as dayafter2,
                (SELECT COUNT()+1 FROM (
                    SELECT DISTINCT date FROM close_cur AS t WHERE date < close_yst2.date)) as rank,
                close as close2
            FROM close_yst2) yst2
    ON cur.rank = yst2.rank-2
    LEFT JOIN 
            (SELECT
                date(date) as daybefore,
                (SELECT COUNT()+1 FROM (
                    SELECT DISTINCT date FROM close_cur AS t WHERE date < close_yst2.date)) as rank,
                close as close_before
            FROM close_yst2) yst3
    ON cur.rank = yst3.rank+1
'''

df = pd.read_sql_query(qry, conn, parse_dates=["date"])
# print(df.head(1104))




date_from = datetime.datetime.strptime(
    'Aug 5 2016', '%b %d %Y').date()
date_to = datetime.date.today()

yec = YahooEarningsCalendar()

list_result = yec.earnings_on(date_from)

df_table = pd.DataFrame(yec.earnings_between(date_from,date_to))

df_table = df_table[['companyshortname','startdatetime','startdatetimetype','ticker']]

print(df_table)


#print(yec.earnings_on(date_from)[])
#print(yec.earnings_between(date_from, date_to))




# data['4. close'].plot()
# plt.title('Intraday Times Series for the MSFT stock (1 min)')
# plt.show()
#
# print("script is running")



# from alpha_vantage.timeseries import TimeSeries
# from alpha_vantage.techindicators import TechIndicators
# from alpha_vantage.sectorperformance import SectorPerformances
# from alpha_vantage.cryptocurrencies import CryptoCurrencies
# import matplotlib
# import matplotlib.pyplot as plt
# import os
# # Make plots bigger
# matplotlib.rcParams['figure.figsize'] = (20.0, 10.0)
#
#
# # ts = TimeSeries(key=os.environ['YCZ9XRMG0CPPQTRG'], output_format='csv')
# # data_csv,_ = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='compact')
# # data_csv
#
# ts = TimeSeries(key='YCZ9XRMG0CPPQTRG', output_format='pandas')
# data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
# # We can describe it
# data.describe()