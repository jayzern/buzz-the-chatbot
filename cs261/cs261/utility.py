import pandas as pd
import json
import urllib.request
import requests
import bs4 as bs
import lxml
import pickle
import cs261.news as news


################################################## Basic Statistics
def get_close_spot_price(ticker):
    df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
    price = df.iloc[-1,4]
    return price

def get_high_spot_price(ticker):
    df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
    price = df.iloc[-1,2]
    return price

def get_low_spot_price(ticker):
    df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
    price = df.iloc[-1,3]
    return price

def get_open_spot_price(ticker):
    df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
    price = df.iloc[-1,1]
    return price

def get_trading_volume(ticker):
    df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
    volume = df.iloc[-1,6]
    return volume

def get_average_trading_volume(ticker):
    df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
    volume = 0
    for i in range(1,5):
        volume += df.iloc[-i,6] # average over 5 days
    return volume/5

def get_percentage_change(ticker):
    df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
    yesterday_close = df.iloc[-2,4]
    today_close = df.iloc[-1,4]
    return (today_close - yesterday_close) * 100 / yesterday_close

def get_value_change(ticker):
    df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
    yesterday_close = df.iloc[-2,4]
    today_close = df.iloc[-1,4]
    return (today_close - yesterday_close)

def get_spot_price_date(ticker, date):
    df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
    row = df[df['Date'] == date]
    price = row.iloc[0,4]
    return price

def get_trading_volume_date(ticker, date):
    df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
    row = df[df['Date'] == date]
    volume = row.iloc[0,6]
    return volume

def get_profit(ticker):
    with urllib.request.urlopen("https://query2.finance.yahoo.com/v10/finance/quoteSummary/"+ticker+".L?modules=financialData") as url:
        data = json.loads(url.read().decode())

    profitMargins = json.dumps(data['quoteSummary']['result'][0]['financialData']['profitMargins']['raw'])
    revenue = json.dumps(data['quoteSummary']['result'][0]['financialData']['totalRevenue']['raw'])
    profit = float(profitMargins) - float(revenue)
    return profit

def get_eps(ticker):
    with urllib.request.urlopen("https://query2.finance.yahoo.com/v10/finance/quoteSummary/"+ticker+".L?modules=defaultKeyStatistics") as url:
        data = json.loads(url.read().decode())

    trailingEps = json.dumps(data['quoteSummary']['result'][0]['defaultKeyStatistics']['trailingEps']['raw'])
    forwardEps = json.dumps(data['quoteSummary']['result'][0]['defaultKeyStatistics']['forwardEps']['raw'])
    return (trailingEps, forwardEps)

# OK this is probably wrong.... idk how to calculate div per share
def get_dividend(ticker):
    with urllib.request.urlopen("https://query2.finance.yahoo.com/v10/finance/quoteSummary/"+ticker+".L?modules=cashflowStatementHistory,defaultKeyStatistics") as url:
        data = json.loads(url.read().decode())

    dividends = json.dumps(data['quoteSummary']['result'][0]['cashflowStatementHistory']['cashflowStatements'][0]['dividendsPaid']['raw'])
    outstandingShares = json.dumps(data['quoteSummary']['result'][0]['defaultKeyStatistics']['sharesOutstanding']['raw'])
    dps = -float(dividends) / float(outstandingShares)
    return dps

################################################## Group Statistics
# Helper Function
def get_tickers(industry):
    resp = requests.get('https://en.wikipedia.org/wiki/FTSE_100_Index')
    soup = bs.BeautifulSoup(resp.text, "lxml")
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        if(row('td')[2].text == industry):
            ticker = row('td')[1].text
            if ticker.endswith('.'):
                ticker = ticker[:-1]
            ticker = ticker.replace('.','-')
            tickers.append(ticker)

    with open("ftse100tickers.pickle", "wb") as f:
        pickle.dump(tickers, f)
    return tickers

def get_industry_trend_weekly(industry):
    tickers = get_tickers(industry)
    industry = 0;
    for ticker in tickers:
        df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
        dayOne = df.iloc[-5,4]
        dayFive = df.iloc[-1,4]
        percentageChange = (dayFive - dayOne) / dayOne * 100
        industry = industry + percentageChange

    industry = industry / len(tickers)

    return industry

def get_industry_trend_daily(industry):
    tickers = get_tickers(industry)
    industry = 0;
    for ticker in tickers:
        df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
        dayOne = df.iloc[-2,4]
        dayFive = df.iloc[-1,4]
        percentageChange = (dayFive - dayOne) / dayOne * 100
        industry = industry + percentageChange

    industry = industry / len(tickers)

    return industry

def get_tickers_industry_trend(industry, trend):
    tickers = get_tickers(industry)
    data = []
    for ticker in tickers:
        df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
        dayOne = df.iloc[-5,4]
        dayFive = df.iloc[-1,4]
        percentageChange = (dayFive - dayOne) / dayOne * 100

         # True - Rising, False - Falling
        if(trend):
            if(percentageChange > 0):
                data.append(ticker)
        else:
            if(percentageChange < 0):
                data.append(ticker)
    return data

################################################## News related stuff.
def get_news_industry(industry):
    # Find the name of the companies in the industry via tickers + scrapper
    tickers = get_tickers(industry)
    companies = []
    for ticker in tickers:
        resp = requests.get('https://en.wikipedia.org/wiki/FTSE_100_Index')
        soup = bs.BeautifulSoup(resp.text, "lxml")
        table = soup.find('table', {'class': 'wikitable sortable'})

        for row in table.findAll('tr')[1:]:
            if(row('td')[1].text == ticker):
                company = row('td')[0].text
                companies.append(company)

        with open("ftse100tickers.pickle", "wb") as f:
            pickle.dump(tickers, f)

    # Not present in news
    signal = False

    # beautiful soup
    # sauce = urllib2.urlopen("http://feeds.reuters.com/reuters/UKBankingFinancial").read() # yahoo rss finance not availabe. use reuters instead
    with urllib.request.urlopen("http://feeds.reuters.com/reuters/UKdomesticNews") as url:
        sauce = url.read().decode()
    soup = bs.BeautifulSoup(sauce, 'xml')

    sentence = ""

    # web scrapping
    for url in soup.find_all('item'):
        title = url.title.text
        desc = url.description.text

        sentence = title + desc

        for company in companies:
            if company in sentence:
                signal = True

    return(signal)

def get_news_stock(ticker):
    return news.get_news(ticker)

def get_sentiment_analysis(ticker):
    return news.get_sentiment_analysis(ticker)


################################################## Comparative queries.
def get_compare_tickers_weekly(tickers, Trend = True):
    currentPercentage = -100;

    #tickers is an array of ticker
    for ticker in tickers:
        df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
        dayOne = df.iloc[-5,4]
        dayFive = df.iloc[-1,4]
        percentageChange = (dayFive - dayOne) / dayFive * 100
        print(percentageChange, ticker)
        if(percentageChange > currentPercentage):
            currentPercentage = percentageChange
            currentTicker = ticker

    return currentTicker

def get_compare_tickers_daily(tickers, Trend = True):
    currentTicker = 0;
    currentPercentage = -100;

    #tickers is an array of ticker #Trend
    for ticker in tickers:
        df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
        dayOne = df.iloc[-2,4]
        dayFive = df.iloc[-1,4]
        percentageChange = (dayFive - dayOne) / dayFive * 100
        print(ticker, percentageChange)
        if(percentageChange > currentPercentage):
            currentPercentage = percentageChange
            currentTicker = ticker

    return currentTicker

def get_compare_tickers_monthly(tickers, Trend = True):

    currentTicker = 0;
    currentPercentage = -100;

    #tickers is an array of ticker #Trend
    for ticker in tickers:
        df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
        dayOne = df.iloc[-30,4]
        dayFive = df.iloc[-1,4]
        percentageChange = (dayFive - dayOne) / dayFive * 100
        if(percentageChange > currentPercentage):
            currentPercentage = percentageChange
            currentTicker = ticker

    return currentTicker

################################################## Subjective queries
# def get_tickers_to_invest(): IDK, this is hard

def get_best_ticker_in_industry(industry):
    tickers = get_tickers(industry)

    currentTicker = 0;
    currentPercentage = -100;

    #tickers is an array of ticker #Trend
    for ticker in tickers:
        df = pd.read_csv("cs261/static/ftse100tickers/"+ticker+".csv")
        dayOne = df.iloc[-365,4]
        dayFive = df.iloc[-1,4]
        percentageChange = (dayFive - dayOne) / dayFive * 100
        if(percentageChange > currentPercentage):
            currentPercentage = percentageChange
            currentTicker = ticker

    return currentTicker
