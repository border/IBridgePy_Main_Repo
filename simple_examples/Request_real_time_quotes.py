# -*- coding: utf-8 -*-

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
        self.symbol='STK.FXI'
        #self.symbol='STK.AAPL'
#        self.symbol='CASH.EUR.USD'
#        self.symbol='FUT.ES.USD.201506'

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
            print self.stime, self.symbol, tickname[tickType], '=', size 
        except:
            pass
        
    def tickPrice(self, TickerId, tickType, price, canAutoExecute):
        '''
        This function will be called once price changes automatically
        '''
        tickname={1:'bid',2:'ask',4:'last',6:'high', 7:'low', 9:'close'}
        try:
            print self.stime, self.symbol, tickname[tickType], '=', price
        except:
            pass

    def realtimeBar(self, TickerId, time, open, high, low, close, volume, wap, count):
        '''
        Updates real time 5-second bars.
        '''
        print 'TickerId: %s, open: %f, high: %f, low: %f, close: %f, volume: %f, wap: %f, count: %d' % (TickerId, open, high, low, close, volume, wap, count)

    def currentTime(self, tm):
        """
        IB C++ API call back function. Return system time in datetime instance
        constructed from Unix timestamp using the USeasternTimeZone from MarketManager
        """
        self.stime = datetime.datetime.fromtimestamp(float(str(tm))) 

    def runStrategy(self):
        if self.state=='first':
            if self.stime!=None:
                self.reqMktData(0, create_contract(self.symbol),'233',False)
                #self.reqRealTimeBars(0, create_contract(self.symbol), 5, 'BID', self.useRTH)
                #self.reqRealTimeBars(0, create_contract(self.symbol), 5, 'ASK', self.useRTH)
                self.reqRealTimeBars(0, create_contract(self.symbol), 5, 'TRADES', self.useRTH)
                print 'Request real time quote',self.stime
                self.state='second'
        if self.state=='second':
            pass
            
            
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
   
