from stockdata import stock_data


# Constant parameters for the evaluation function.
DAY_50_WEIGHT = 0.5
DAY_200_WEIGHT = 0.5
PRICE_BOOK_LIMIT = 1.5
PRICE_BOOK_WEIGHT = 5
DIVIDEND_YIELD_WEIGHT = 3
PEG_LIMIT = 1.5
PEG_WEIGHT = 10
PFE_LIMIT = 1.5
PFE_WEIGHT = 10
LOW_SCORE = -10000

'''
Utility function for converting a given string to float or 0.
'''
def to_float(s):
    try:
        f = float(s)
        return f
    except ValueError:
        return 0
        
'''
Class capturing the parameters used in evaluating stocks.
'''
class StockMetrics(object):

    def __init__(self, price, day_50_avg, day_200_avg, pe, pb, dy, ps, peg, EPS_next_year): 
    
        self.price = to_float(price)                    # Current price.
        self.day_50_avg = to_float(day_50_avg)          # 50 day moving average of the price.
        self.day_200_avg = to_float(day_200_avg)        # 200 day moving average of the price.
        self.pe = to_float(pe)                          # Price-earnings ratio.
        self.pb = to_float(pb)                          # Price-book ratio.
        self.dy = to_float(dy)                          # Dividend yield.
        self.ps = to_float(ps)                          # Price-sales ratio.
        self.peg = to_float(peg)                        # Price-earnings to growth ratio.
        self.EPS_next_year = to_float(EPS_next_year)    # Next year's estimate of the earnings per share.

'''
Returns a list of scores for stocks represented by the given list of stock tickers.
'''
def get_stock_scores(stock_tickers):

    # Gets metrics data for the stocks.
    stocks = stock_data.get_current(stock_tickers)
    
    # For each stock,
    stock_scores = []
    for stock in stocks:
    
        # converts metrics data to metrics object,
        stock_metrics = StockMetrics(stock['lasttradepriceonly'], stock['fiftydaymovingaverage'], stock['twohundreddaymovingaverage'], stock['peratio'], stock['pricebook'], stock['dividendyield'], stock['pricesales'], stock['pegratio'], stock['epsestimatenextyear'])
        
        # calculates and adds the score.
        stock_scores.append(evaluate_stock(stock_metrics))
    
    return stock_scores

'''
Returns score (float) of a stock for recommendations based on its metrics.
'''
def evaluate_stock(stock_metrics):
 
    score = 0
    
    # If company is bankrupt return very low score.
    if (stock_metrics.price == 0):
        return LOW_SCORE
    
    # Add points based on the 50 day moving average and current price difference ratio.
    day_50_percentage_difference = (stock_metrics.price - stock_metrics.day_50_avg)/stock_metrics.price
    score += day_50_percentage_difference * DAY_50_WEIGHT

    # Add points based on the 200 day moving average and current price difference ratio.

    day_200_percentage_difference = (stock_metrics.price - stock_metrics.day_200_avg)/stock_metrics.price
    score += day_200_percentage_difference * DAY_200_WEIGHT
    
    # Add points based on price-book (pb) ratio.       
    if (stock_metrics.pb < PRICE_BOOK_LIMIT) :
        score += (PRICE_BOOK_LIMIT - stock_metrics.pb) * PRICE_BOOK_WEIGHT
        
    # Add points based on price-sales (ps) ratio, shouldn't be zero.
    if (stock_metrics.ps != 0):
        if stock_metrics.ps < 2:
            score += 4 - 2 * stock_metrics.ps
        elif stock_metrics.ps > 4.5:
            score += 4.5 - 2 * stock_metrics.ps
        
    # Add points based on dividend yield (dy).
    if (stock_metrics.dy < 6):
        score += stock_metrics.dy * DIVIDEND_YIELD_WEIGHT

    # Add points based on price-earnings (pe) ratio, if ratio is zero, then the stock is loosing money and bad investment.
    if (stock_metrics.pe == 0):
        score += LOW_SCORE
    elif stock_metrics.pe < 15:
        score += 15 - stock_metrics.pe
    elif stock_metrics.pe > 25:
        score += 25 - stock_metrics.pe

    # Add points based on price-earnings to growth (peg) ratio, if ratio is zero, then the stock is loosing money and bad investment.
    if (stock_metrics.peg == 0):
        score += -5
    elif stock_metrics.peg < PEG_LIMIT :
        score += (PEG_LIMIT - stock_metrics.peg) * PEG_WEIGHT

    # Calculate price - forward earnings ration based on EPS next year's estimate, and adds points based on it,
    # evaluates only if there is EPS prediction.
    if (stock_metrics.EPS_next_year != 0):
        pfe = stock_metrics.price / stock_metrics.EPS_next_year
        if pfe < PFE_LIMIT : 
            score += pfe * PFE_WEIGHT
    
    return score