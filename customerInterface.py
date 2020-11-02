import pgdb


class DBContext:

    def __init__(self):

        params = {'host': 'nestor2.csc.kth.se', 'user': input("Username: "), 'database': '', 'password': input("Password: ")}
        self.conn = pgdb.connect(**params)
        self.menu = ["Shipments Status", "Exit"]
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
                print("Invalid choice.")
            except (NameError, ValueError, TypeError, SyntaxError):
                print("meh")

    def shipments(self):
        try:
            # Check that input is integer
            ID = int(input("customerID: "))
        except (NameError, ValueError, TypeError, SyntaxError):
            print("Non numerical ID. Try again...")
            return

        # Good against SQL injections attacks because escape characters are removed
        fname = pgdb.escape_string(input("First Name: ").strip())
        lname = pgdb.escape_string(input("Last Name: ").strip())

        query = "SELECT first_name, last_name FROM customers WHERE customer_id = %s;" % ID
        print(query)
        print("------------------------------------------------------------")

        try:
            self.cur.execute(query)
        except (NameError, ValueError, TypeError, SyntaxError):
            print("Query execution failed.")
            return

        customer_list = self.cur.fetchone()
        if customer_list is None:
            print("Customer does not exist in DB")
            return
        else:
            if customer_list[0].lower() == fname.lower() and customer_list[1].lower() == lname.lower():
                print("Welcome %s %s" % (fname, lname))
            else:
                print("Name %s %s does not match %s" % (
                    fname, lname, ID))  # ID exists but first name or/and last name are incorrect
                return

        # isbn alone is ambigous because it's a key to 2 tables (stock,shipments)
        # and for that reason it must be specified on which table the SQL should check
        query = """SELECT shipment_id,ship_date,shipments.isbn,title          
                   FROM Shipments                                   
                        JOIN editions ON shipments.isbn = editions.isbn
                        JOIN books ON editions.book_id = books.book_id
                    WHERE customer_id = %s; """ % ID

        print("------------------------------------------------------------")
        try:
            self.cur.execute(query)
            print("Customer: %d | %s | %s" % (ID, fname, lname))
            print("shipment_id, ship_date, isbn, title")
            self.print_answer()
        except (NameError, ValueError, TypeError, SyntaxError):
            print("Query execution failed.")
            return
        print("------------------------------------------------------------\n")

    def exit(self):
        self.cur.close()
        self.conn.close()
        exit()

    def print_answer(self):
        print("\n".join([", ".join([str(a) for a in x]) for x in self.cur.fetchall()]))

    def run(self):

        actions = [self.shipments, self.exit]

        while True:
            try:
                actions[self.print_menu() - 1]()
            except IndexError:
                print("Bad choice")
                continue


if __name__ == "__main__":
    db = DBContext()
    db.run()
