from stockstalker.models import Index, Stock

import stock_data

'''
Used when refreshing the list of stocks in a particular index. 
Sort the fetched and existing lists of stocks into lists of stocks that should be added, kept and removed. 
Assumes that stocks in "existing" has been retrieved from DB such that it can actually be removed.
'''
def filter_index_members(fetched, existing):
    
    add = []
    keep = []
    remove = []

    for f in fetched:
        found = False
        for e in existing:
            if f.ticker == e.ticker:
                found = True
                existing.remove(e)
                continue

        if found:
            keep.append(f)
        else:
            add.append(f)

    return (add, keep, existing)


''' 
Downloads members of the specified STOCK INDEX.
Compares to rows in database containing STOCKS in that INDEX.
Adds those not already in database to database.
Removes those found in database but not found in list of downloaded members of STOCK INDEX.
'''
def update(indexname):
    
    # Index name is not equal to string needed to scrape data from Yahoo. 
    # Find that string before scraping. 
    try:
        index = Index.objects.get(symbol=indexname)
    except ObjectDoesNotExist:
        return 'Stock ' + indexname + ' not valid.'
    
    # Scrape - takes a few seconds:
    scraped = stock_data.get_index_members(index.fetch_string)
    fetched = [Stock(index=index, ticker=x['ticker'], name=x['company']) for x in scraped]
    
    # Select all stocks with the same index id.
    try:
        existing = list(Stock.objects.filter(index=index))
    except Stock.DoesNotExist:
        existing = []
    
    # Sort into lists
    (add, keep, remove) = filter_index_members(fetched, existing)

    # Add necessary items
    for a in add:
        a.save()

    # Remove extra stocks. Relationships with users' stocks are automatically handled. 
    for r in remove:
        r.delete()

    return 'Added: ' + str(len(add)) + "\n" + 'Deleted: ' + str(len(remove))
