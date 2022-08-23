import sqlite3

class DBHelper:
    def __init__(self, dbname="trackings"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS trackings(chatid integer, url text, opcion text, estado text)"
        prodids = "CREATE INDEX IF NOT EXISTS prodID ON trackings(url ASC)"
        userids = "CREATE INDEX IF NOT EXISTS userID ON trackings(chatid ASC)"
        self.conn.execute(stmt)
        self.conn.execute(prodids)
        self.conn.execute(userids)
        self.conn.commit()

    def add_tracking(self,chatid,url,opcion,estado):
        stmt = "INSERT INTO trackings(chatid, url, opcion, estado) values(?,?,?,?)"
        args = (chatid, url, opcion, estado)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def del_tracking(self, url, chatid):
        stmt = "DELETE FROM trackings WHERE url = (?) AND chatid = (?)"
        args = (url, chatid)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_trackings(self, chatid):
        stmt = "SELECT url FROM trackings WHERE chatid = (?)"
        args = (chatid, )
        return [x[0] for x in self.conn.execute(stmt, args)]

# if __name__ == "__main__":
#     db = DBHelper()
#     db.setup()