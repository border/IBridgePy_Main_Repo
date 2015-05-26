# For this example, we're going to write a simple momentum script.  
# When the price starts to go up, we're going to buy; 
# when it starts to go down, we're going to sell.  
# Hopefully we'll ride the waves.

# To run an algorithm in IBridgePy, you need two functions: 
# initialize and handle_data.

def initialize(context):
    # The initialize function sets any data or variables that 
    # you'll use in your algorithm. 
    # For instance, you'll want to define the security 
    # (or securities) you want to trade.  
    # You'll also want to define any parameters or values 
    # you're going to use later. 
    # It's only called once at the beginning of your algorithm.
    
    # In our example, we'll track the stock price of AAPL every minute.
    # In the strategy, we are going to use historical prices of 10-min bars 
    # so that we specifiy them in initialize function

    context.security=symbol('CASH.EUR.USD')
    #context.securities=symbols('CASH.EUR.USD', 'CASH.AUD.USD')
    #context.security=symbol('STK.AAPL.USD')
    #context.security=symbols('STK.AAPL.USD', 'STK.FB.USD')
    context.hist_frame=['1 min']

# The handle_data function is where the real work is done.  
# This function is run every minute 
# You can change it to run at other frequencies and we help you get it done
def handle_data(context, data):
    
    # To make market decisions, we're calculating the stock's 
    # moving average for the open price of the last 30 10-min bars
    # and its current price. 

    current_price = data[context.security].bid_price


    # To calcuate moving average, I simply searched the python code of the 
    # indicators of moving average using google and it showed up.
    # The funciton of moving average is placed behind handle_data function
    mv_5_n1=moving_average(data[context.security].hist['1 min']['open'],5)[-1] 
    mv_5_n2=moving_average(data[context.security].hist['1 min']['open'],5)[-2] 
    mv_30_n1=moving_average(data[context.security].hist['1 min']['open'],30)[-1] 
    mv_30_n2=moving_average(data[context.security].hist['1 min']['open'],30)[-2] 
    
    print get_datetime()
    print 'current price', current_price
    print 'mv_5_n1=',mv_5_n1, 'mv_30_n1=',mv_30_n1
    print 'mv_5_n2=',mv_5_n2, 'mv_30_n2=',mv_30_n2

    
    # We have a powerful portfolio object.
    # The portfolio object tracks your positions, cash,
    # cost basis of specific holdings, and more.  In this line, we calculate
    # the current amount of cash in our portfolio.   
    cash = context.portfolio.cash


    # Here is the meat of our strategy.
    # If the average price of 5 10-min bars starts to increase to 
    # above the average price of 30 10-min bars 
    # AND we have enough cash, then we will place a long order.
    # If the average price of 5 10-min bars starts to drop to 
    # below the average price of 30 10-min bars 
    # then we want to close our position to 0 shares.
    if mv_5_n1 > mv_30_n1 and mv_5_n2 < mv_30_n2:

        # Need to calculate how many shares we can buy
        number_of_shares = int(cash/current_price)

        # Place the buy order (positive means buy, negative means sell)
        #order(context.security, +number_of_shares)
        print 'Buy ' + context.security + ' ' + number_of_shares + '@' + current_price

    elif mv_5_n1<mv_30_n1 and mv_5_n2 > mv_30_n2:
        
        # Sell all of our shares by setting the target position to zero
        #order_target(context.security, 0)
        print 'Sell all stock @' + current_price



# This is the funciton of calculating moving average. 
# I searched online and it showed up.
# If you want to use other indicators, just google it. You will find it quickly
# That is the beauty of Python. Thank to all who have contributed
# many to the Python world
# You may ignore the following line if you are not interested in the details of
# calculating the indicator of moving average
def moving_average(x, n, type='simple'):
    """
    compute an n period moving average.

    type is 'simple' | 'exponential'

    """
    import numpy as np
    x = np.asarray(x)
    if type=='simple':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()


    a =  np.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a
