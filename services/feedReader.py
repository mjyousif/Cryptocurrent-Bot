import feedparser


# ----------------------------
# A class!
class Articles:
    def __init__(self, title, link, description=""):
        self.title = title
        self.link = link
        self.description = description


# ----------------------------
def getBetween(stringIn, before, after, beforeFix=0, afterFix=0):
    stringBeforeIndex = stringIn.find(before) + beforeFix
    # print(stringBeforeIndex)
    stringAfterIndex = stringIn.find(after) + afterFix
    stringOut = stringIn[stringBeforeIndex:stringAfterIndex]
    # print (stringOut)
    return stringOut


def news(tag=None):
    results = []
    openEntries = 10

    url = [
        "https://www.coindesk.com/feed/",
        "https://cointelegraph.com/rss",
        "http://themerkle.com/feed/",
    ]
    urlLen = len(url)
    i = 0
    for i in range(urlLen):
        if openEntries > 0:
            feed = feedparser.parse(url[i])
            if tag is None:
                k = 0
                for k in range(
                    len(feed["entries"])
                    if len(feed["entries"]) < openEntries
                    else openEntries
                ):
                    results.append(
                        Articles(
                            feed["entries"][k]["title"],
                            feed["entries"][k]["link"],
                            feed["entries"][k]["summary_detail"]["value"],
                        )
                    )
            else:
                matchedEntries = []
                for k in range(len(feed["entries"])):
                    entry = feed["entries"][k]
                    tag_lower = tag.lower()
                    matched = False

                    if "tags" in entry:
                        for n in range(len(entry["tags"])):
                            if tag_lower == entry["tags"][n]["term"].lower():
                                matched = True
                                break

                    if not matched:
                        if "title" in entry and tag_lower in entry["title"].lower():
                            matched = True
                        elif (
                            "summary_detail" in entry
                            and tag_lower
                            in entry["summary_detail"].get("value", "").lower()
                        ):
                            matched = True

                    if matched:
                        matchedEntries.append(k)
                k = 0
                for k in range(
                    len(matchedEntries)
                    if len(matchedEntries) < openEntries
                    else openEntries
                ):
                    results.append(
                        Articles(
                            feed["entries"][matchedEntries[k]]["title"],
                            feed["entries"][matchedEntries[k]]["link"],
                        )
                    )
                    if url[i] == "https://www.coindesk.com/feed/":
                        results[-1].description = feed["entries"][matchedEntries[k]][
                            "summary_detail"
                        ]["value"]
                    elif url[i] == "https://cointelegraph.com/rss":
                        results[-1].description = getBetween(
                            feed["entries"][k]["summary_detail"]["value"],
                            "<p>",
                            "</p>",
                            3,
                            0,
                        )
                    elif url[i] == "http://themerkle.com/feed/":
                        results[-1].description = getBetween(
                            feed["entries"][matchedEntries[k]]["summary_detail"][
                                "value"
                            ],
                            "/>",
                            "</p>",
                            2,
                            0,
                        )

            openEntries = openEntries - len(results)
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
