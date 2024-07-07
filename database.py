import json
from datetime import datetime, timedelta
from typing import NamedTuple
import aiofiles
import aiosqlite


class Lot(NamedTuple):
    url: str
    description: str
    price: str
    created: str


class DataBase:
    def __init__(self, name) -> None:
        self.name = name

    async def get_lots_json(self):
        async with aiofiles.open("data/lots.json", "r", encoding="utf-8") as f:
            result = await f.read()
            lots = json.loads(result)
            return lots

    @staticmethod
    def str_date(date=datetime.now()):
        return datetime.strftime(date, "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def org_date(date_str: str):
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    async def insert_all_data(self):
        data = await self.get_lots_json()
        lots = [
            Lot(
                lot.get("url"),
                lot.get("description"),
                lot.get("price"),
                self.str_date(),
            )
            for lot in data
        ]
        await self._insert_lots(lots)

    async def check_data(self, url):
        async with aiosqlite.connect(self.name) as conn:
            cur = await conn.execute("SELECT * FROM lots WHERE url = ?", (url,))
            result = await cur.fetchone()
            return bool(result)

    async def insert_new_lots(self) -> list[Lot]:
        lots = await self.get_lots_json()
        new_lots = [
            Lot(
                url=lot.get("url"),
                description=lot.get("description"),
                price=lot.get("price"),
                created=self.str_date(),
            )
            for lot in lots
            if not await self.check_data(lot.get("url"))
        ]
        await self._insert_lots(new_lots)
        return new_lots

    async def _insert_lots(self, lots: list[Lot]):
        async with aiosqlite.connect(self.name) as conn:
            await conn.executemany(
                "INSERT INTO lots(url, description, price, created) VALUES(?, ?, ?, ?)",
                [tuple(lot) for lot in lots],
            )
            await conn.commit()

    async def delete_old_lots(self):
        month_ago = datetime.now() - timedelta(days=7)

        async with aiosqlite.connect(self.name) as conn:
            lots_base = await conn.execute(
                "SELECT url, description, price, created FROM lots"
            )
            lots = [Lot(*lot) for lot in await lots_base.fetchall()]
            old_lot_urls = []
            for lot in lots:
                if lot.created is None or self.org_date(lot.created) < month_ago:
                    old_lot_urls.append((lot.url,))

            await conn.executemany("DELETE FROM lots WHERE url = ?", old_lot_urls)
            await conn.commit()
