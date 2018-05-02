import bs4 as bs
import urllib.request
import json

from nltk.sentiment.util import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# mkdir ./nltk_data
# python -m nltk.downloader
# Set Download Directory in GUI
nltk.data.path.append('./nltk_data/')

#ticker = raw_input("Enter Stock Ticker Symbol (i.e. AAPL, FB, TSLA):\n")
#ticker = "FB"

class Article:
    def __init__(self, title, desc, link, pubDate):
        self.title = title
        self.desc = desc
        self.link = link
        self.pubDate = pubDate

# beautiful soup
def get_news(ticker):
	with urllib.request.urlopen("https://feeds.finance.yahoo.com/rss/2.0/headline?s="+ticker+".L") as url:
		sauce = url.read().decode()
	soup = bs.BeautifulSoup(sauce, 'xml')

	data = []

	# web scrapping
	for url in soup.find_all('item'):
		title = url.title.text
		desc = url.description.text
		link = url.link.text
		pubDate = url.pubDate.text

		#article = {'title': title, 'desc': desc, 'link': link, 'pubDate': pubDate }
		data.append(Article(title, desc, link, pubDate))
		#sentences.append(title + ". " + desc)

	# dump data into json file
	return data


def get_sentiment_analysis(ticker):
	articles = get_news(ticker)

	# Sentiment Intensity Analysis for each individual news article title + brief description
	# can be improved if entire article is used instead?
	sentiment = []
	sid = SentimentIntensityAnalyzer()
	print(sid)
	for i in range(0,len(articles)):
		ss = sid.polarity_scores(articles[i].title +","+ articles[i].desc)
		sentiment.append(ss)
		#for k in sorted(ss):
		#	print('{0}: {1}, '.format(k, ss[k]))
		#print()
	return sentiment