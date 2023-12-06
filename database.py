import json
import sqlite3


class DataBase:
    def __init__(self, name) -> None:
        self.connect = sqlite3.connect(name)
        self.cursor = self.connect.cursor()
    
    def get_lots_json(self):
        with open("data/lots.json", "r") as f:
            lots = json.load(f)
            return lots

    def insert_all_data(self):
        lots = self.get_lots_json()
        for lot in lots:
            with self.connect:
                self.cursor.execute(
                    "INSERT INTO lots(url, description, price) VALUES(?, ?, ?)",
                    (lot.get("url"), lot.get("description"), lot.get("price")),
                )

    def check_data(self, url):
        with self.connect:
            cur = self.cursor.execute('SELECT * FROM lots WHERE url = ?', (url, ))
            result = cur.fetchone()
            return bool(result)

    def insert_lots(self):
        lots = self.get_lots_json()
        new_lots = []
        for lot in lots:
            if not self.check_data(lot.get('url')):
                with self.connect:
                    self.cursor.execute('INSERT INTO lots(url, description, price) VALUES(?, ?, ?)', 
                                            (lot.get('url'), lot.get('description'), lot.get('price')))
                new_lots.append(lot)
        return new_lots
                        
