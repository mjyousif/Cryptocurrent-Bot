import asyncio
from types import SimpleNamespace
from app import inline_crypto


class DummyInlineQuery:
    def __init__(self, query):
        self.query = query
        self.answered = None

    async def answer(self, results, **kwargs):
        self.answered = results
        print("Answered with", len(results), "result(s)")
        for r in results:
            print(" -", getattr(r, "title", repr(r)))


class DummyUpdate:
    def __init__(self, query):
        self.inline_query = DummyInlineQuery(query)


async def run():
    upd = DummyUpdate("bitcoin,ethereum")
    await inline_crypto(upd, None)


if __name__ == "__main__":
    asyncio.run(run())
