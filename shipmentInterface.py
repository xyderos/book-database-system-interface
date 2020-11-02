import pgdb


class DBContext:

    def __init__(self):

        params = {'host': 'nestor2.csc.kth.se', 'user': input("Username: "), 'database': '',
                  'password': input("Password: ")}
        self.conn = pgdb.connect(**params)
        self.menu = ["Record a shipment", "Show stock", "Show shipments", "Exit"]
        self.cur = self.conn.cursor()

    def print_menu(self):

        for i, x in enumerate(self.menu):
            print("%i. %s" % (i + 1, x))
        return self.get_int()

    def get_int(self):

        while True:

            try:
                choice = int(input("Choose: "))

                if 1 <= choice <= len(self.menu):
                    return choice

            except (NameError, ValueError, TypeError, SyntaxError):
                print("meh")

    def makeShipments(self):

        try:

            CID = int(input("cutomerID: "))

            SID = int(input("shipment ID: "))

            isbn = pgdb.escape_string((input("isbn: ").strip()))

            date = pgdb.escape_string(input("Ship date: ").strip())

        except (NameError, ValueError, TypeError, SyntaxError):
            return

        query = "SELECT stock FROM stock WHERE isbn='%s';" % (isbn)

        try:

            self.cur.commit()

            self.cur.execute("set transaction isolation level serializable")
            try:
                self.cur.execute(query)
            except(pgdb.DatabaseError, pgdb.OperationalError):
                return

            stock_result = self.cur.fetchone()
            if stock_result is None:
                return

            cnt = stock_result[0];
            if cnt < 1:
                return
            else:

                query = """UPDATE stock SET stock=stock-1 WHERE isbn='%s';""" % isbn
                self.cur.execute(query)


            query = """INSERT INTO shipments VALUES (%i, %i, '%s','%s');""" % (SID, CID, isbn, date)

            try:
                self.cur.execute(query)  # execute insert
            except (pgdb.DatabaseError, pgdb.OperationalError):
                return

            self.conn.commit()

        except (pgdb.DatabaseError, pgdb.OperationalError) as e:

            self.conn.rollback()

            return

    def showStock(self):

        query = """SELECT * FROM stock;"""

        try:
            self.cur.execute(query)
        except (pgdb.DatabaseError, pgdb.OperationalError):
            self.conn.rollback()
            return

        self.print_answer()

    def showShipments(self):

        query = """SELECT * FROM shipments;"""
        try:
            self.cur.execute(query)
        except (pgdb.DatabaseError, pgdb.OperationalError):

            self.conn.rollback()
            return
        self.print_answer()

    def exit(self):
        self.cur.close()
        self.conn.close()
        exit()

    def print_answer(self):
        print("\n".join([", ".join([str(a) for a in x]) for x in self.cur.fetchall()]))

    def run(self):

        actions = [self.makeShipments, self.showStock, self.showShipments, self.exit]
        while True:
            try:
                actions[self.print_menu() - 1]()
            except IndexError:
                continue


if __name__ == "__main__":
    db = DBContext()
    db.run()