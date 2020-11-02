import pgdb

from functools import reduce


class DBContext:

    def __init__(self):

        params = {'host': 'nestor2.csc.kth.se', 'user': input("Username: "), 'database': input("Database: "), 'password': input("Password: ")}

        self.conn = pgdb.connect(**params)

        self.menu = ["Select.", "Insert.", "Remove.", "Exit"]

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

    def select(self):

        tables = [x.strip() + " natural join " for x in input("Choose table(s): ").split(",")]

        tables[len(tables) - 1] = tables[len(tables) - 1][0:len(tables[len(tables) - 1]) - 14]

        columns = input("Choose column(s): ")

        filters = input("Apply filters: ")
        try:
            query = """SELECT %s FROM %s%s;""" % (

                reduce(lambda a, b: a + b, columns), "".join(tables), "" if filters == "" else " WHERE %s" % filters)

        except (NameError, ValueError, TypeError, SyntaxError):
            return

        self.cur.execute(query)

        self.print_answer()

    def remove(self):

        table = input("\nTable to delete: ")

        column = input("Column to delete: ")

        value = input("Value of column to delete: ")
        try:
            query = "DELETE FROM %s WHERE %s = %s;" % (table, column, value)

        except (NameError, ValueError, TypeError, SyntaxError):
            return

        self.cur.execute(query)

        self.conn.commit()

        query = "SELECT * FROM %s;" % (table)
        self.cur.execute(query)
        print("\n--------------------------------------")
        self.print_answer_new()
        print("----------------------------------------")

    def insert(self):
        table = input("\nEnter table you wish to insert into: ")
        columns = input("Enter the columns that you wish to add to separated by commas: ")
        values = input("Enter the values you wish to enter separated by commas: ")

        try:
            query = "INSERT INTO %s (%s) VALUES (%s);" % (table, columns, values)
        except (NameError, ValueError, TypeError, SyntaxError):
            return

        self.cur.execute(query)
        self.conn.commit()

    def exit(self):
        self.cur.close()
        self.conn.close()
        exit()

    def print_answer(self):
        print("\n".join([", ".join([str(a) for a in x]) for x in self.cur.fetchall()]))

    def print_answer_new(self):
        print("\n".join([" | ".join([str(a) for a in x]) for x in self.cur.fetchall()]))

    def run(self):

        actions = [self.select, self.insert, self.remove, self.exit]

        while True:
            try:
                actions[self.print_menu() - 1]()

            except IndexError:

                print("Bad choice")


if __name__ == "__main__":
    db = DBContext()
    db.run()
