import sqlite3

class DBHelper:
    def __init__(self, dbname="trackings_dbms"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS trackings(chatid integer, url text, titulo text, opcion text, estado text)"
        prodids = "CREATE INDEX IF NOT EXISTS prodID ON trackings(url ASC)"
        userids = "CREATE INDEX IF NOT EXISTS userID ON trackings(chatid ASC)"
        self.conn.execute(stmt)
        self.conn.execute(prodids)
        self.conn.execute(userids)
        self.conn.commit()

    # Añade un nuevo producto para ser rastreado
    def add_tracking(self,chatid,url,titulo,opcion,estado):
        stmt = "INSERT INTO trackings(chatid, url, titulo, opcion, estado) values(?,?,?,?,?)"
        args = (chatid, url, titulo, opcion, estado)
        self.conn.execute(stmt, args)
        self.conn.commit()

    # Elimina un producto que esta siendo rastreado
    def del_tracking(self, url, chatid):
        stmt = "DELETE FROM trackings WHERE url = (?) AND chatid = (?)"
        args = (url, chatid)
        self.conn.execute(stmt, args)
        self.conn.commit()

    # Obtiene los productos en rastreo dado un usuario
    def get_trackings(self, chatid):
        stmt = "SELECT titulo FROM trackings WHERE chatid = (?)"
        args = (chatid, )
        return [x[0] for x in self.conn.execute(stmt, args)]

    # Obtiene el titulo de un producto dada su URL
    def get_title(self, url):
        stmt = "SELECT titulo FROM trackings WHERE url = (?)"
        args = (url, )
        return self.conn.execute(stmt, args)

    # Obtiene la URL de un producto dado su titulo
    def get_url(self, titulo):
        stmt = "SELECT url FROM trackings WHERE titulo = (?)"
        args = (titulo, )
        return self.conn.execute(stmt, args).fetchall()

    def get_all(self):
        stmt = "SELECT * FROM trackings"
        return self.conn.execute(stmt).fetchall()

    def update_estado(self, status, chat_id, url):
        stmt = "UPDATE trackings SET estado = (?) WHERE chatid = ? AND url = ?"
        args = (status, chat_id, url)
        self.conn.execute(stmt, args)
        self.conn.commit()


# if __name__ == "__main__":
#     db = DBHelper()
#     db.setup()