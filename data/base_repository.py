class BaseRepository:
    def __init__(self, db):
        self.db = db

    def execute(self, query: str, params: tuple = ()):
        cursor = self.db.cursor()
        cursor.execute(query, params)
        self.db.commit()
        return cursor

    def fetch_one(self, query: str, params: tuple = ()):
        cursor = self.db.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple = ()):
        cursor = self.db.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()