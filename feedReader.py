import feedparser

#----------------------------
#A class!
class Articles:
    def __init__(self, title, link, description):
        self.title=title
        self.link=link
        self.description=description


#----------------------------



def news(tag=None):
    url = "https://www.coindesk.com/feed/"
    feed = feedparser.parse(url)
    # print(feed['entries'][0]['tags'])
    results=[]
    if (tag==None):
        k=0
        for k in range(len(feed['entries'])):
            results.append(Articles(feed['entries'][k]['title'],feed['entries'][k]['link'],feed['entries'][k]['summary_detail']['value']))
    else:
        matchedEntries=[]
        k=0
        for k in range(len(feed['entries'])):
            i=0
            for i in range(len(feed['entries'][k]['tags'])):
                if (tag.lower()==feed['entries'][k]['tags'][i]['term'].lower()):
                    matchedEntries.append(k)
                # print("    "+feed['entries'][k]['tags'][i]['term'])
        k=0
        for k in range(len(matchedEntries)):
            results.append(Articles(feed['entries'][matchedEntries[k]]['title'],feed['entries'][matchedEntries[k]]['link'],feed['entries'][matchedEntries[k]]['summary_detail']['value']))

    return results


