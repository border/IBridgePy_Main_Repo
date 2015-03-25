#!/usr/bin/env python

import IBCpp
import time
import datetime
import pandas as pd

def create_contract(security):
    if security.split('.')[0]=='FUT':
        contract = IBCpp.Contract()
        contract.symbol = security.split('.')[1]
        contract.secType = 'FUT'
        contract.exchange = 'GLOBEX'
        contract.currency = security.split('.')[2]
        contract.expiry= security.split('.')[3]
        contract.primaryExchange='GLOBEX'
    elif security.split('.')[0]=='CASH':
        contract = IBCpp.Contract()
        contract.symbol = security.split('.')[1]
        contract.secType = 'CASH'
        contract.exchange = 'IDEALPRO'
        contract.currency = security.split('.')[2]
        contract.primaryExchange='IDEALPRO'
    elif security.split('.')[0]=='STK':
        contract = IBCpp.Contract()
        contract.symbol = security.split('.')[1]
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'
        contract.primaryExchange='SMART'
    return contract 

class MyClient(IBCpp.IBClient) :    
    def setup(self):
        self.symbol='STK.AAPL'
#        self.symbol='CASH.EUR.USD'
#        self.symbol='FUT.ES.USD.201506'
        self.hist = pd.DataFrame(columns = 
            ['symbol', 'open','high','low','close', 
             'volume', 'barCount', 'WAP'])
        self.request_hist_data_status = None
        self.currentHistSymbol = ""
        self.stime=None
        self.state='first'
        
    def error(self, errorId, errorCode, errorString):
        print 'errorId = ' + str(errorId), 'errorCode = ' + str(errorCode)
        print 'error message: ' + errorString
        
    def request_hist_data(self, contract, endDateTime, durationStr, barSizeSetting):   
        self.currentHistSymbol = contract.symbol+contract.currency
        if contract.secType=='STK' or contract.secType=='FUT':
            self.reqHistoricalData(0, contract, endDateTime , 
                                   durationStr, barSizeSetting, 'TRADES', 1, 1)

        if contract.secType=='CASH':
            self.reqHistoricalData(0, contract, endDateTime , 
                                   durationStr, barSizeSetting, 'BID', 1, 1)
        print 'Request historical data', self.stime
        self.request_hist_data_status='Submitted'
        
    def historicalData(self, reqId, date, price_open, price_high, price_low, 
                       price_close, volume, barCount, WAP, hasGaps):
        if reqId==0:           
            if 'finished' in str(date):
                self.request_hist_data_status='Done'
            else: 
                if '  ' in date: # Two datetime structues may come back
                    date=datetime.datetime.strptime(date, '%Y%m%d  %H:%M:%S')                        
                else:
                    date=datetime.datetime.strptime(date, '%Y%m%d') 
                if date in self.hist.index: # Write data to self.hist
                    self.hist['symbol'][date] = self.currentHistSymbol
                    self.hist['open'][date]=price_open
                    self.hist['high'][date]=price_high
                    self.hist['low'][date]=price_low
                    self.hist['close'][date]=price_close
                    self.hist['volume'][date] = volume
                    self.hist['barCount'][date] = barCount
                    self.hist['WAP'][date] = WAP
                else:
                    newRow = pd.DataFrame({'open':price_open,'high':price_high,
                                           'low':price_low,'close':price_close, 
                                           'volume': volume, 'barCount': barCount, 
                                           'WAP': WAP,
                                           'symbol': self.currentHistSymbol},
                                          index = [date])
                    self.hist=self.hist.append(newRow)

    def currentTime(self, tm):
        """
        IB C++ API call back function. Return system time in datetime instance
        constructed from Unix timestamp using the USeasternTimeZone from MarketManager
        """
        self.stime = datetime.datetime.fromtimestamp(float(str(tm))) 

    def runStrategy(self):
        if self.state=='first':
            if self.stime!=None:
                req = datetime.datetime.strftime(self.stime,"%Y%m%d %H:%M:%S") #datatime -> string                print dt_stime                
                c.request_hist_data(create_contract(self.symbol), req, '1 W', '1 day')
                self.state='second'
        if self.state=='second':
            if self.request_hist_data_status=='Done':
                print self.hist
                print 'COMPLETED'
                exit()
        
if __name__ == '__main__' :
    # connect to IB
    port = 7496; clientID = 1
    c = MyClient()
    c.setup()
    c.connect("", port, clientID)

    # request server time    
    c.reqCurrentTime()
    
    while(1):
        time.sleep(1)
        c.processMessages()
        c.runStrategy()
        c.reqCurrentTime()
   