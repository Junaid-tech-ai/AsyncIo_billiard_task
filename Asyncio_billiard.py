import json
import aiohttp
import argparse
import asyncio
from datetime import datetime
from billiard import Pool


GOOGLE_SUGGEST_API_URL = (
    "http://suggestqueries.google.com/complete/search?client=firefox&q={}"
)


async def fetch_suggestions(keyword, session):
    async with session.get(GOOGLE_SUGGEST_API_URL.format(keyword)) as response:
        suggestions = await response.text()
        suggestions = json.loads(suggestions)[1]
        return suggestions


def is_misspelled(keyword, suggestions):
    if not suggestions:
        return True
    if keyword in suggestions or len(keyword) <= 2:
        return False

    shortest_suggestion = min(suggestions, key=len)
    keyword_words = keyword.split()
    suggestion_words = shortest_suggestion.split()

    if not suggestions or len(keyword_words) > len(suggestion_words):
        return True

    for i in range(len(keyword_words)):
        if keyword_words[i] != suggestion_words[i]:
            return True

    return False


def process_keywords(keyword):
    async def main():
        async with aiohttp.ClientSession() as session:
            suggestions = await fetch_suggestions(keyword, session)
            misspelled = is_misspelled(keyword, suggestions)

        result = {
            "keyword": keyword,
            "misspelled": misspelled,
            "suggestions": suggestions
        }

        result_json = json.dumps(result, indent=4)

        print(result_json)

    asyncio.run(main())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("keywords", nargs="+")
    args = parser.parse_args()

    start = datetime.now()

    with Pool() as pool:
        pool.map(process_keywords, args.keywords)

    end = datetime.now()
    print(end - start)
