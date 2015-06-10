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
        #self.symbol='STK.FXI'
        self.symbol='STK.AAPL'
        #self.symbol='CASH.EUR.USD'
        #self.symbol='FUT.ES.USD.201506'

        #better to read these from a file
        self.contractlist = pd.DataFrame([
            ['STK.AAPL'],
            ['STK.FB'],
            ['STK.TWTR']
            ])

        # make decent column names
        self.contractlist.columns = ['sym']

        #add these specific column names to match the name returned by TickType.getField()
        self.contractlist['bidPrice'] = 0
        self.contractlist['askPrice'] = 0
        self.contractlist['lastPrice'] = 0

        self.state='first'
        self.useRTH=0
        
    def error(self, errorId, errorCode, errorString):
        print 'errorId = ' + str(errorId), 'errorCode = ' + str(errorCode)
        print 'error message: ' + errorString

    def tickSize(self, TickerId, tickType, size):
        '''
        This function is called when the market data changes. Sizes are updated immediately with no delay
        '''
        tickname={0:'bidSize', 3:'askSize', 5:'lastSize', 8:'volumeSize'}
        try:
            print self.stime, TickerId, self.contractlist.loc[TickerId]['sym'], tickname[tickType], '=', size 
        except:
            pass
        
    def tickPrice(self, TickerId, tickType, price, canAutoExecute):
        '''
        This function will be called once price changes automatically
        '''
        tickname={1:'bid',2:'ask',4:'last',6:'high', 7:'low', 9:'close'}
        try:
            print self.stime, TickerId, self.contractlist.loc[TickerId]['sym'], tickname[tickType], '=', price
        except:
            pass

    def realtimeBar(self, TickerId, time, open, high, low, close, volume, wap, count):
        '''
        Updates real time 5-second bars.
        '''
        #print 'TickerId: %s, open: %f, high: %f, low: %f, close: %f, volume: %f, wap: %f, count: %d' % (self.contractlist.loc[TickerId]['sym'], open, high, low, close, volume, wap, count)
        print 'TickerId: %s, open: %f, high: %f, low: %f, close: %f, volume: %f, wap: %f, count: %d' % (TickerId, open, high, low, close, volume, wap, count)
        #print 'TickerId: %s, open: %f, high: %f, low: %f, close: %f, volume: %f, wap: %f, count: %d' % (self.symbol, open, high, low, close, volume, wap, count)

    def currentTime(self, tm):
        """
        IB C++ API call back function. Return system time in datetime instance
        constructed from Unix timestamp using the USeasternTimeZone from MarketManager
        """
        self.stime = datetime.datetime.fromtimestamp(float(str(tm))) 

    def runStrategy(self):
        if self.state=='first':
            if self.stime!=None:
                #self.reqMktData(0, create_contract(self.symbol),'233',False)
                #self.reqRealTimeBars(0, create_contract(self.symbol), 5, 'BID', self.useRTH)
                #self.reqRealTimeBars(0, create_contract(self.symbol), 5, 'ASK', self.useRTH)
                #self.reqRealTimeBars(0, create_contract(self.symbol), 5, 'TRADES', self.useRTH)
                self.reqRealTimeBars(1, create_contract(self.symbol), 5, 'TRADES', self.useRTH)
                print 'Request real time quote',self.stime
                self.state='second'
                for index, row in self.contractlist.iterrows():
                    #print 'Index:', index, ', Sym:', row['sym']
                    #self.reqMktData(index, create_contract(row['sym']),'233',False)
                    #self.reqRealTimeBars(index, create_contract(row['sym']), 5, 'TRADES', self.useRTH)
                    #self.reqRealTimeBars(index, create_contract('STK.AAPL'), 5, 'TRADES', self.useRTH)
                    break

        if self.state=='second':
            pass
            
            
if __name__ == '__main__' :
    # connect to IB
    port = 7496; clientID = 3
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
   
