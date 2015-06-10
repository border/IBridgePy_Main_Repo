# -*- coding: utf-8 -*-
import pandas as pd

import IBCpp 
import datetime
import time

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

class MyClient(IBCpp.IBClient):
    def setup(self):
        self.stime=None

        #better to read these from a file
        self.contractlist = pd.DataFrame([
            ['STK.AAPL', 0, 0, 0],
            ['STK.FB', 0, 0, 0],
            ['STK.TWTR', 0, 0, 0]
            ])

        # make decent column names
        self.contractlist.columns = ['sym', 'bidPrice', 'askPrice', 'lastPrice']

        self.state='first'
        self.useRTH=0
        
    def error(self, errorId, errorCode, errorString):
        print 'errorId = ' + str(errorId), 'errorCode = ' + str(errorCode)
        print 'error message: ' + errorString

    def tickPrice(self, TickerId, tickType, price, canAutoExecute):
        '''
        This function will be called once price changes automatically
        '''
        tickname={1:'bid',2:'ask',4:'last',6:'high', 7:'low', 9:'close'}
        try:
            if tickType == 1 or tickType == 2 or tickType == 4:
                print self.stime, TickerId, self.contractlist.loc[TickerId]['sym'], tickname[tickType], '=', price
            '''
            if tickType == 1:
                self.contractlist.loc[TickerId, 'bidPrice'] = price
            elif tickType == 2: 
                self.contractlist.loc[TickerId, 'askPrice'] = price
            elif tickType == 4:
                self.contractlist.loc[TickerId, 'lastPrice'] = price
            else:
                pass
            '''
        except:
            pass

    def currentTime(self, tm):
        """
        IB C++ API call back function. Return system time in datetime instance
        constructed from Unix timestamp using the USeasternTimeZone from MarketManager
        """
        self.stime = datetime.datetime.fromtimestamp(float(str(tm))) 

    def runStrategy(self):
        if self.state=='first':
            if self.stime!=None:
                print 'Request real time quote',self.stime
                self.state='second'
                for index, row in self.contractlist.iterrows():
                    print 'Index:', index, ', Sym:', row['sym']
                    self.reqMktData(index, create_contract(row['sym']), '233', False)

            
if __name__ == '__main__' :
    # connect to IB
    port = 7496; clientID = 999
    c = MyClient()
    c.setup()
    c.connect("", port, clientID)

    # request server time    
    c.reqCurrentTime()
    
    while(1):
        time.sleep(5)
        c.processMessages()
        c.runStrategy()
        c.reqCurrentTime()
   
