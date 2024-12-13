import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import cx_Oracle

# Database connection setup
username = "lab9"
password = "abc123"  # Replace with the correct password
dsn = "//localhost:1521/xe"
connection = cx_Oracle.connect(username, password, dsn)
cursor = connection.cursor()

class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("900x700")
        self.admin_password = "admin123"

        self.main_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_window()

        header_frame = tk.Frame(self.root, bg="skyblue", height=80)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="Library Management System", font=("Arial", 24, "bold"), bg="skyblue").pack(pady=20)

        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)

        ttk.Button(main_frame, text="Admin Login", command=self.admin_login, width=30).pack(pady=15)
        ttk.Button(main_frame, text="Student/Teacher Panel", command=self.student_teacher_panel, width=30).pack(pady=15)
        ttk.Button(main_frame, text="Exit", command=self.root.quit, width=30).pack(pady=15)

    def admin_login(self):
        self.clear_window()

        frame = tk.Frame(self.root, bg="white")
        frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)

        tk.Label(frame, text="Admin Login", font=("Arial", 20, "bold"), bg="white").pack(pady=20)

        tk.Label(frame, text="Enter Password:", font=("Arial", 12), bg="white").pack(pady=5)
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.pack(pady=10)

        ttk.Button(frame, text="Login", command=self.verify_admin).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.main_menu).pack(pady=10)

    def verify_admin(self):
        password = self.password_entry.get()
        if password == self.admin_password:
            self.admin_panel()
        else:
            messagebox.showerror("Error", "Incorrect admin password.")

    def admin_panel(self):
        self.clear_window()

        header_frame = tk.Frame(self.root, bg="lightgreen", height=80)
        header_frame.pack(fill=tk.X)

        tk.Label(header_frame, text="Admin Panel", font=("Arial", 24, "bold"), bg="lightgreen").pack(pady=20)

        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)

        button_style = {"width": 30, "padding": 10}
        
        ttk.Button(main_frame, text="Add Book", command=self.add_book_window, **button_style).pack(pady=10)
        ttk.Button(main_frame, text="Display Books", command=self.display_books, **button_style).pack(pady=10)
        ttk.Button(main_frame, text="Add Member", command=self.add_member_window, **button_style).pack(pady=10)
        ttk.Button(main_frame, text="Display Members", command=self.display_members, **button_style).pack(pady=10)
        ttk.Button(main_frame, text="Display Borrowings", command=self.display_borrowings, **button_style).pack(pady=10)
        ttk.Button(main_frame, text="Back to Main Menu", command=self.main_menu, **button_style).pack(pady=10)

    def student_teacher_panel(self):
        self.clear_window()

        frame = tk.Frame(self.root, bg="white")
        frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)

        tk.Label(frame, text="Student/Teacher Panel", font=("Arial", 20, "bold"), bg="white").pack(pady=20)

        ttk.Button(frame, text="Borrow Book", command=self.borrow_book_window, width=30).pack(pady=10)
        ttk.Button(frame, text="Return Book", command=self.return_book_window, width=30).pack(pady=10)
        ttk.Button(frame, text="Back to Main Menu", command=self.main_menu, width=30).pack(pady=10)

    def borrow_book_window(self):
        self.clear_window()
        self.create_form("Borrow Book", self.borrow_book, ["Book ID", "Member ID", "Borrow Date (YYYY-MM-DD)", "Due Date (YYYY-MM-DD)"])

    def borrow_book(self, entries):
        try:
            # Auto-generate Borrow ID
            cursor.execute("SELECT NVL(MAX(BORROW_ID), 0) + 1 FROM BORROW")
            borrow_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO BORROW (BORROW_ID, BOOK_ID, MEMBER_ID, BORROW_DATE, DUE_DATE)
                VALUES (:1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD'), TO_DATE(:5, 'YYYY-MM-DD'))
                """,
                [borrow_id] + entries
            )
            connection.commit()
            messagebox.showinfo("Success", f"Book borrowed successfully! Borrow ID: {borrow_id}")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            messagebox.showerror("Error", f"Database error: {error.message}")

    def return_book_window(self):
        self.clear_window()
        self.create_form("Return Book", self.return_book, ["Borrow ID", "Return Date (YYYY-MM-DD)"])

    def return_book(self, entries):
        try:
            cursor.execute(
                """
                UPDATE BORROW SET RETURN_DATE = TO_DATE(:2, 'YYYY-MM-DD') WHERE BORROW_ID = :1
                """,
                entries
            )
            connection.commit()
            messagebox.showinfo("Success", "Book returned successfully!")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            messagebox.showerror("Error", f"Database error: {error.message}")

    def create_form(self, title, submit_command, labels, back_command=None):
        tk.Label(self.root, text=title, font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        entries = []
        for label in labels:
            tk.Label(self.root, text=label, font=("Arial", 12), bg="white").pack(pady=5)
            entry = ttk.Entry(self.root)
            entry.pack(pady=5)
            entries.append(entry)

        ttk.Button(self.root, text="Submit", command=lambda: submit_command([entry.get() for entry in entries])).pack(pady=20)
        ttk.Button(self.root, text="Back", command=back_command or self.main_menu).pack(pady=10)

    def add_book_window(self):
        self.clear_window()
        self.create_form("Add Book", self.add_book, ["Book ID", "Title", "Author", "Publisher", "Genre", "Year of Publication (YYYY-MM-DD)", "Status"], back_command=self.admin_panel)

    def add_book(self, entries):
        try:
            cursor.execute(
                """
                INSERT INTO BOOKS (BOOK_ID, TITLE, AUTHOR_ID, PUBLISHER_ID, GENRE, YEAROFPUBLICATION, STATUS)
                VALUES (:1, :2, :3, :4, :5, TO_DATE(:6, 'YYYY-MM-DD'), :7)
                """,
                entries
            )
            connection.commit()
            messagebox.showinfo("Success", "Book added successfully!")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            messagebox.showerror("Error", f"Database error: {error.message}")

    def add_member_window(self):
        self.clear_window()
        self.create_form("Add Member", self.add_member, ["Member ID", "Name", "Contact Details", "Member Type"], back_command=self.admin_panel)

    def add_member(self, entries):
        try:
            cursor.execute(
                """
                INSERT INTO MEMBER (MEMBER_ID, NAME, CONTACT_DETAILS, MEMBER_TYPE)
                VALUES (:1, :2, :3, :4)
                """,
                entries
            )
            connection.commit()
            messagebox.showinfo("Success", "Member added successfully!")
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            messagebox.showerror("Error", f"Database error: {error.message}")

    def display_books(self):
        self.display_table("Books", "SELECT * FROM BOOKS", ["Book ID", "Title", "Author", "Publisher", "Genre", "Year", "Status"], format_dates=[5])

    def display_members(self):
        self.display_table("Members", "SELECT * FROM MEMBER", ["Member ID", "Name", "Contact", "Type"])

    def display_borrowings(self):
        self.display_table("Borrowings", "SELECT * FROM BORROW", ["Borrow ID", "Book ID", "Member ID", "Borrow Date", "Due Date", "Return Date"], format_dates=[3, 4, 5])

    def display_table(self, title, query, headers, format_dates=None):
        self.clear_window()

        tk.Label(self.root, text=title, font=("Arial", 20, "bold"), bg="white").pack(pady=10)

        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tree = ttk.Treeview(frame, columns=headers, show="headings")
        for header in headers:
            tree.heading(header, text=header)
            tree.column(header, width=150, anchor="center")

        tree.pack(fill=tk.BOTH, expand=True)

        try:
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                if format_dates:
                    row = list(row)
                    for index in format_dates:
                        if row[index]:
                            row[index] = row[index].strftime('%d-%m-%Y')
                tree.insert("", tk.END, values=row)

        except cx_Oracle.DatabaseError as e:
            error, = e.args
            messagebox.showerror("Error", f"Database error: {error.message}")

        ttk.Button(self.root, text="Back", command=self.admin_panel).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryGUI(root)
    root.mainloop()
