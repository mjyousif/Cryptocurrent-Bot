import feedparser

#----------------------------
#A class!
class Articles:
    def __init__(self, title, link, description=""):
        self.title=title
        self.link=link
        self.description=description


#----------------------------
def getBetween(stringIn, before, after,beforeFix=0,afterFix=0):
    stringBeforeIndex=stringIn.find(before)+beforeFix
    # print(stringBeforeIndex)
    stringAfterIndex=stringIn.find(after)+afterFix
    stringOut=stringIn[stringBeforeIndex:stringAfterIndex]
    # print (stringOut)
    return stringOut



def news(tag=None):
    results=[]
    openEntries=10
    
    url=["https://www.coindesk.com/feed/",'https://cointelegraph.com/rss','http://themerkle.com/feed/']
    urlLen=len(url)
    i=0
    for i in range(urlLen):
        if openEntries>0:
                feed = feedparser.parse(url[i])
                if (tag==None):
                    k=0
                    for k in range(len(feed['entries']) if len(feed['entries'])<openEntries else openEntries):
                        results.append(Articles(feed['entries'][k]['title'],feed['entries'][k]['link'],feed['entries'][k]['summary_detail']['value']))
                else:
                    matchedEntries=[]
                    k=0
                    for k in range(len(feed['entries'])):
                        n=0
                        for n in range(len(feed['entries'][k]['tags'])):
                            if (tag.lower()==feed['entries'][k]['tags'][n]['term'].lower()):
                                matchedEntries.append(k)
                            # print("    "+feed['entries'][k]['tags'][i]['term'])
                    k=0
                    for k in range(len(matchedEntries) if len(matchedEntries)<openEntries else openEntries):
                        results.append(Articles(feed['entries'][matchedEntries[k]]['title'],feed['entries'][matchedEntries[k]]['link']))
                        if url[i]=="https://www.coindesk.com/feed/":
                            results[-1].description=feed['entries'][matchedEntries[k]]['summary_detail']['value']
                        elif url[i]=='https://cointelegraph.com/rss':
                            results[-1].description=getBetween(feed['entries'][k]['summary_detail']['value'],'<p>','</p>',3,0)
                        elif url[i]=='http://themerkle.com/feed/':
                            results[-1].description=getBetween(feed['entries'][matchedEntries[k]]['summary_detail']['value'],'/>','</p>',2,0)
                        
                openEntries=openEntries-len(results)
    return results        

    
# results=news('bitcoin')
# # print((len(results)))    
# i=0    
# for i in range(len(results)):
    # print('-----------'+str(i)+'-----------')
    # print(results[i].title)
    # print(results[i].link)
    # print(results[i].description)
    # print('-----------------------')
    # # getBetween(news()[0].description,'<p>','</p>')


