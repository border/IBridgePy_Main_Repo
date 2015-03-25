# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 13:50:41 2015

@author: IBridgePy

DISCLAIMER
_________________________________________________________
All information provided is for educational purposes only.
_________________________________________________________

There is a risk of loss in stocks, futures, forex and options trading. Please 
trade with capital you can afford to lose. Past performance is not necessarily
indicative of future results. Nothing in this computer program/code is intended
to be a recommendation to buy or sell any stocks or futures or options market. 
All information and computer programs provided is for education and entertainment
purpose only; accuracy and thoroughness cannot be guaranteed. Readers/users
are soly responsible for how they use the information and for their results.

You may change the code in any way and distribute it. But you may not 
change or remove the disclaimer. 
"""



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

def create_order(action,amount,orderType, price=None): 
    import IBCpp
    order = IBCpp.Order()
    order.action = action      # BUY, SELL
    order.totalQuantity = amount
    order.orderType =  orderType  #LMT, MKT, STP
    order.tif='GTC'
    order.transmit = True 
    if orderType=='MKT':
        return order
    elif orderType=='LMT':    
        order.lmtPrice=price
        return order

class MyClient(IBCpp.IBClient):
    def setup(self):
        self.stime=None
        self.nextId=0
#        self.symbol='STK.AAPL'
#        self.symbol='CASH.EUR.USD'
        self.symbol='FUT.ES.USD.201506'

        self.state='first'
        
#    def error(self, errorId, errorCode, errorString):
#        print 'errorId = ' + str(errorId), 'errorCode = ' + str(errorCode)
#        print 'error message: ' + errorString

    def nextValidId(self, id):
        self.nextId=id
        
    def currentTime(self, tm):
        """
        IB C++ API call back function. Return system time in datetime instance
        constructed from Unix timestamp using the USeasternTimeZone from MarketManager
        """
        self.stime = datetime.datetime.fromtimestamp(float(str(tm))) 

    def orderStatus(self,orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld):
        """
        call back function of IB C++ API which update status or certain order
        indicated by orderId
        """
        print self.symbol, status, 'filled=',filled, 'remaining=', remaining 
        
    def runStrategy(self):
        if self.state=='first':
            if self.stime!=None:
                self.placeOrder(self.nextId, create_contract(self.symbol), \
                                   create_order('BUY', 100, 'MKT'))
                print 'Request to place an order',self.stime
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