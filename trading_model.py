#from IPython.core.display import display, HTML
#display(HTML("<style>.container { width:100% !important; }</style>"))
import pandas as pd
import os
from datetime import datetime
#historical_data_file = os.getcwd() + '/historicalData.csv'
#his_df = pd.read_csv(historical_data_file)
source_price_data_file = os.getcwd() + '/scr/simResult/simResults-2019.csv'
#df0=pd.read_csv(historical_data_file)
print ('loading {}'.format(source_price_data_file))
df = pd.read_csv(source_price_data_file)
print ('shape of source file {}'.format(df.shape))
print ('source data header:')
for i in df:
    print (i, end=' ')
daily_supply_charge = 0.924   # $ /day
general_usage_rates = 31.79  # cents /kWh
solar_feed_in = 0.111    # $ /kWh exported
price_file = os.getcwd() + '/scr/priceData/Price_data_2018.csv'
print ('\nloading {}'.format(price_file))
priceData = pd.read_csv(price_file)
#model 1: (old model)
#1. From the historical data, we can compute the following variables:
#AQmax=maximum(Main grid price) 
AQmax = max(priceData.spot_price)      # get 2.4645200000000003
#print ('AQmax = ', AQmax)
user_id_max = max(df.user_id)             #the numbr of user_id in the priceData 14? 500?
#print ('max user id number %s'%user_id_max)
number_Time_step = int(len(df) / user_id_max)
#print ('number_Time_step %s'%number_Time_step)
netCostprosumer = []
for i in range (0, number_Time_step):   
    df_ = df[i*user_id_max : (i+1)*user_id_max]     
    netCostprosumer.append(sum(df_.purchase) - sum(df_.feed_in))
netCostMin = min(netCostprosumer)       
netCostMax = max(netCostprosumer)        
#print ('netCostMax {},netCostMin {}'.format(netCostMax, netCostMin))  
#NetcostMin=minimum(∑_prosumers▒〖purchased 〗-∑_prosumers▒〖feedin 〗)
#2. With the real-time feed-in and purchased of 500 prosumers, the Feed-in price is computed as:
#esp model:
#feedInPrice = 
#0.01+0.6(CurrentNetCost-min(-6811779.069,CurrentNetCost))/(max(1488583.836,CurrentNetCost)-min(-6811779.069,CurrentNetCost))*(0.1-0.01)
print ('creating feed in price...')
feedInPrice = []
feedInTarrif = 0.1116
for i in range (0, number_Time_step):
    df_ = df[i*user_id_max: (i +1)* user_id_max]
    currentNetCost = sum(df_.purchase) - sum(df_.feed_in)
    Q = feedInTarrif + 0.05*(currentNetCost - min(netCostMin,currentNetCost)) / (max(netCostMax, currentNetCost) - min(netCostMin, currentNetCost)) * (AQmax-feedInTarrif)    
    feedInPrice.append(Q)   
#	Function / Method 2 – to calculate the real-time cost of a specified prosumer (Netcost_prosumer) if the price plan is implemented;
#Netcost_prosumer=retail_price*purchased_prosumer-Q*feedin_prosumer
#	Function / Method 3 – to calculate the real-time benefit of the DSP (Bene_DSP) if the price plan is implemented.
#Bene_DSP=1.3*(selling price*∑_prosumers▒〖purchased 〗-(main grid price*maximum(0,∑_prosumers▒〖purchased 〗-∑_prosumers▒〖feedin 〗)+Q*∑_prosumers▒〖feedin 〗))
print ('creating sum feed in ...')
sumPurchased=[]
sumFeedIn=[]
BeneDSP = []
for i in range (0,number_Time_step):
    df_ = df[i*user_id_max: (i +1)* user_id_max]
    #df_ = df.loc[df['user_id'] == id_number]   
    sumPurchased.append(sum(df_.purchase))
    sumFeedIn.append(sum(df_.feed_in))
#print(len(priceData.retail_price), len(sumPurchased), len(priceData.spot_price),len(sumFeedIn),len(feedInPrice))
currentTimeMax=len(sumPurchased)
print ("calculating BeneDSP")
BeneDSP=[]
for i in range (0,number_Time_step):
    temp = 1.3*(priceData.retail_price[i]*sumPurchased[i] - (priceData.spot_price[i]*(max(0,sumPurchased[i]-sumFeedIn[i])+feedInPrice[i]*sumFeedIn[i])))
    BeneDSP.append(temp)                
#print ('len of BeneDSP %s'%len(BeneDSP))
#3. With the real-time selling price, the feed-in and purchased of a prosumer and the computed feed-in price Q, the real-time cost of the prosumer is computed as:
#Netcost_prosumer=selling price*purchased_prosumer-Q*feedin_prosumer
NetCost = []
temp=[]
customer_flag = []
print ("Calculating NetCost...")
for id_number in range (1,user_id_max+1):
    df_ = df.loc[df['user_id'] == id_number]   
    if max(df_.pv_generation) == 0: 
        customer_flag.append(0)
    else:
        customer_flag.append(1)  
    #print(len(priceData.retail_price ), len(df_.purchase),len(feedInPrice),len(df_.feed_in) )
    temp = priceData.retail_price * df_.purchase.values - feedInPrice* df_.feed_in.values    
    NetCost.append(temp.values)
customer_flag_ = []
for j in range(len(customer_flag)):
    for i in range(number_Time_step):
        customer_flag_.append(customer_flag[j])
#NetCost
print ('creating customer Net Cost csv...')
table3= []
for a in range(len(NetCost[1])):
    for b in range(len(NetCost)):        
        dic = {'CostNet':NetCost[b][a], 'customer_id':b,'BeneDSP':BeneDSP[a], 'FeedInPrice': feedInPrice[a],
               'retailPrice':priceData.retail_price[a],'spot_price':priceData.spot_price[a],'custFlag':customer_flag[b]
              }
        table3.append(dic)        
print ('convert tabe to data frame...')
table3_df = pd.DataFrame(table3)   
table3_df['customer_flag'] = pd.DataFrame(customer_flag_)
print ('completed convertion.')
"""
beneDSP_list = []
feedInPrice_list = []
retailPrice_list = []
spotPrice_list = []
custFlag_list = []
table3=[]
table3_df = pd.DataFrame(table3)
for a in range(user_id_max):    
    for b in range(number_Time_step):        
        custFlag_list.append(customer_flag[a])
        beneDSP_list.append(BeneDSP[b]) 
        feedInPrice_list.append(feedInPrice[b])
        retailPrice_list.append(priceData.retail_price[b])
        spotPrice_list.append(priceData.spot_price[b]        
print ('build a dataframe table3_df to include the results of the trading model along with the prices used and customer flag')
table3_df['beneDSP'] = pd.DataFrame(beneDSP_list) 
table3_df['feedInPrice'] = pd.DataFrame(feedInPrice_list)  
table3_df['retailPrice'] = pd.DataFrame(retailPrice_list)
table3_df['spotPrice'] = pd.DataFrame(spotPrice_list)
table3_df['custFlag'] = pd.DataFrame(custFlag_list) 
"""
print ('build a dataframe table3_df to include the results of the trading model along with the prices used and customer flag')
print ('table3_df is built')
df2 = pd.concat([df,table3_df], axis = 1, join_axes = [df.index])
"""
for id_number in range (user_id_max):
    df_ = df2.loc[df2['customer_id'] == id_number]
    print(id_number,sum(df_.custFlag))
"""
print ('saving df2 to file result_in_time_step.csv')
data_directory = os.getcwd() + '/result/'
if not os.path.exists(data_directory):
    os.makedirs(data_directory)
outPutFile = data_directory + 'result_in_time_step.csv'
df2.to_csv(outPutFile, encoding='utf-8', index = False)
print ("result_in_time_step.csv file created. Program completed.")