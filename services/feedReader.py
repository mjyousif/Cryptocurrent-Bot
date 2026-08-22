import re

import feedparser


# ----------------------------
# A class!
class Articles:
    def __init__(self, title, link, description=""):
        self.title = title
        self.link = link
        self.description = description


# ----------------------------
def clean_html(text: str) -> str:
    """Removes HTML tags from the given string."""
    if not text:
        return ""
    # Remove HTML tags using regex
    return re.sub(r"<[^>]+>", "", text).strip()


def news(tag=None):
    results = []
    openEntries = 10

    url = [
        "https://www.coindesk.com/feed/",
        "https://cointelegraph.com/rss",
        "http://themerkle.com/feed/",
    ]
    urlLen = len(url)

    for i in range(urlLen):
        if openEntries > 0:
            feed = feedparser.parse(url[i])
            if tag is None:
                for k in range(
                    len(feed["entries"])
                    if len(feed["entries"]) < openEntries
                    else openEntries
                ):
                    raw_desc = (
                        feed["entries"][k].get("summary_detail", {}).get("value", "")
                    )
                    results.append(
                        Articles(
                            feed["entries"][k]["title"],
                            feed["entries"][k]["link"],
                            clean_html(raw_desc),
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

                for k in range(
                    len(matchedEntries)
                    if len(matchedEntries) < openEntries
                    else openEntries
                ):
                    raw_desc = (
                        feed["entries"][matchedEntries[k]]
                        .get("summary_detail", {})
                        .get("value", "")
                    )
                    results.append(
                        Articles(
                            feed["entries"][matchedEntries[k]]["title"],
                            feed["entries"][matchedEntries[k]]["link"],
                            clean_html(raw_desc),
                        )
                    )

            openEntries = openEntries - len(results)

    return results
