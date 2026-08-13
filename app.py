from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, datetime, timedelta
import os


# ============================================================
# LIBRARYPRO - LIBRARY MANAGEMENT SYSTEM
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "librarypro-secret-key-2026"
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "database": os.environ.get("DB_NAME", "library_db"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get(
        "DB_PASSWORD",
        "Taha@12345"
    ),
    "port": os.environ.get("DB_PORT", "5432")
}


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_database():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        # ----------------------------------------------------
        # USERS TABLE
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                userid SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                fullname VARCHAR(150),
                role VARCHAR(50) DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


              # ----------------------------------------------------
        # ISSUES TABLE - COMPATIBILITY COLUMNS
        # ----------------------------------------------------

        cursor.execute("""
            ALTER TABLE issues
            ADD COLUMN IF NOT EXISTS issuedate DATE
        """)

        cursor.execute("""
            ALTER TABLE issues
            ADD COLUMN IF NOT EXISTS duedate DATE
        """)

        cursor.execute("""
            ALTER TABLE issues
            ADD COLUMN IF NOT EXISTS returndate DATE
        """)

        cursor.execute("""
            ALTER TABLE issues
            ADD COLUMN IF NOT EXISTS issue_date DATE
        """)

        cursor.execute("""
            ALTER TABLE issues
            ADD COLUMN IF NOT EXISTS due_date DATE
        """)

        cursor.execute("""
            ALTER TABLE issues
            ADD COLUMN IF NOT EXISTS return_date DATE
        """)

        cursor.execute("""
            ALTER TABLE issues
            ADD COLUMN IF NOT EXISTS fine NUMERIC(10,2) DEFAULT 0
        """)

        cursor.execute("""
            ALTER TABLE issues
            ADD COLUMN IF NOT EXISTS status VARCHAR(30)
            DEFAULT 'Issued'
        """)

        cursor.execute("""
            ALTER TABLE issues
            ADD COLUMN IF NOT EXISTS created_at
            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """)

        # ----------------------------------------------------
        # MAKE LEGACY DATE COLUMNS OPTIONAL
        # ----------------------------------------------------

        cursor.execute("""
            ALTER TABLE issues
            ALTER COLUMN issuedate DROP NOT NULL
        """)

        cursor.execute("""
            ALTER TABLE issues
            ALTER COLUMN duedate DROP NOT NULL
        """)

        cursor.execute("""
            ALTER TABLE issues
            ALTER COLUMN returndate DROP NOT NULL
        """)

        # ----------------------------------------------------
        # MAKE NEW DATE COLUMNS OPTIONAL FOR OLD RECORDS
        # ----------------------------------------------------

        cursor.execute("""
            ALTER TABLE issues
            ALTER COLUMN issue_date DROP NOT NULL
        """)

        cursor.execute("""
            ALTER TABLE issues
            ALTER COLUMN due_date DROP NOT NULL
        """)

        cursor.execute("""
            ALTER TABLE issues
            ALTER COLUMN return_date DROP NOT NULL
        """)









































































































        # ----------------------------------------------------
        # BOOKS TABLE
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                bookid SERIAL PRIMARY KEY,
                isbn TEXT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT,
                publisher TEXT,
                publishyear INTEGER,
                quantity INTEGER NOT NULL DEFAULT 1,
                availablequantity INTEGER NOT NULL DEFAULT 1,
                year INTEGER,
                available INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # EXISTING BOOKS TABLE COLUMNS
        # ----------------------------------------------------

        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN IF NOT EXISTS isbn TEXT
        """)

        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN IF NOT EXISTS title TEXT
        """)

        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN IF NOT EXISTS author TEXT
        """)

        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN IF NOT EXISTS category TEXT
        """)

        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN IF NOT EXISTS publisher TEXT
        """)

        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN IF NOT EXISTS publishyear INTEGER
        """)

        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1
        """)

        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN IF NOT EXISTS availablequantity INTEGER DEFAULT 1
        """)

        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN IF NOT EXISTS year INTEGER
        """)

        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN IF NOT EXISTS available INTEGER DEFAULT 1
        """)

        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN IF NOT EXISTS created_at
            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """)

        # ----------------------------------------------------
        # BOOK ID SEQUENCE
        # ----------------------------------------------------

        cursor.execute("""
            CREATE SEQUENCE IF NOT EXISTS books_bookid_seq
        """)

        cursor.execute("""
            ALTER TABLE books
            ALTER COLUMN bookid
            SET DEFAULT nextval('books_bookid_seq')
        """)

        cursor.execute("""
            ALTER SEQUENCE books_bookid_seq
            OWNED BY books.bookid
        """)

        # ----------------------------------------------------
        # MEMBERS TABLE
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                memberid SERIAL PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                email VARCHAR(150),
                phone VARCHAR(50),
                address TEXT,
                membership_date DATE DEFAULT CURRENT_DATE,
                status VARCHAR(30) DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # ISSUES TABLE
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                issueid SERIAL PRIMARY KEY,

                bookid INTEGER NOT NULL
                REFERENCES books(bookid)
                ON DELETE CASCADE,

                memberid INTEGER NOT NULL
                REFERENCES members(memberid)
                ON DELETE CASCADE,

                issue_date DATE DEFAULT CURRENT_DATE,

                due_date DATE,

                return_date DATE,

                fine NUMERIC(10,2) DEFAULT 0,

                status VARCHAR(30) DEFAULT 'Issued',

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # DEFAULT ADMIN
        # ----------------------------------------------------

        cursor.execute("""
            SELECT userid
            FROM users
            WHERE username = %s
        """, ("admin",))

        admin = cursor.fetchone()

        if admin is None:

            cursor.execute("""
                INSERT INTO users
                (
                    username,
                    password,
                    fullname,
                    role
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                "admin",
                "admin123",
                "Library Administrator",
                "admin"
            ))

        conn.commit()

        print("Database initialized successfully.")

    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "Database initialization error:",
            e
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# LOGIN
# ============================================================

@app.route("/", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()

        if not username or not password:

            flash(
                "Please enter username and password.",
                "danger"
            )

            return render_template("login.html")

        conn = None
        cursor = None

        try:

            conn = get_db_connection()

            cursor = conn.cursor(
                cursor_factory=RealDictCursor
            )

            cursor.execute("""
                SELECT
                    userid,
                    username,
                    password,
                    fullname,
                    role
                FROM users
                WHERE username = %s
                AND password = %s
            """, (
                username,
                password
            ))

            user = cursor.fetchone()

            if user:

                session["user_id"] = user["userid"]
                session["username"] = user["username"]
                session["fullname"] = user["fullname"]
                session["role"] = user["role"]

                return redirect(
                    url_for("dashboard")
                )

            flash(
                "Invalid username or password.",
                "danger"
            )

        except Exception as e:

            print(
                "Login error:",
                repr(e)
            )

            flash(
                "Database connection error.",
                "danger"
            )

        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()

    return render_template("login.html")

# # ============================================================
# # DASHBOARD
# # ============================================================

# @app.route("/dashboard")
# def dashboard():

#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     conn = None
#     cursor = None

#     try:

#         conn = get_db_connection()

#         cursor = conn.cursor(
#             cursor_factory=RealDictCursor
#         )

#         # ====================================================
#         # TOTAL BOOKS
#         # ====================================================

#         cursor.execute("""
#             SELECT
#                 COALESCE(SUM(quantity), 0) AS total
#             FROM books
#         """)

#         total_books = cursor.fetchone()["total"]

#         # ====================================================
#         # AVAILABLE BOOKS
#         # ====================================================

#         cursor.execute("""
#             SELECT
#                 COALESCE(SUM(availablequantity), 0) AS total
#             FROM books
#         """)

#         available_books = cursor.fetchone()["total"]

#         # ====================================================
#         # TOTAL MEMBERS
#         # ====================================================

#         cursor.execute("""
#             SELECT
#                 COUNT(*) AS total
#             FROM members
#         """)

#         total_members = cursor.fetchone()["total"]

#         # ====================================================
#         # ISSUED BOOKS
#         # ====================================================

#         cursor.execute("""
#             SELECT
#                 COUNT(*) AS total
#             FROM issues
#             WHERE status = 'Issued'
#         """)

#         issued_books = cursor.fetchone()["total"]

#         # ====================================================
#         # RETURNED BOOKS
#         # ====================================================

#         cursor.execute("""
#             SELECT
#                 COUNT(*) AS total
#             FROM issues
#             WHERE status = 'Returned'
#         """)

#         returned_books = cursor.fetchone()["total"]

#         # ====================================================
#         # OVERDUE BOOKS
#         # ====================================================

#         cursor.execute("""
#             SELECT
#                 COUNT(*) AS total
#             FROM issues
#             WHERE status = 'Issued'
#             AND due_date < CURRENT_DATE
#         """)

#         overdue_books = cursor.fetchone()["total"]

#         # ====================================================
#         # TOTAL FINES
#         # ====================================================

#         cursor.execute("""
#             SELECT
#                 COALESCE(SUM(fine), 0) AS total
#             FROM issues
#         """)

#         total_fines = cursor.fetchone()["total"]

#         # ====================================================
#         # RECENT TRANSACTIONS
#         # ====================================================

#         cursor.execute("""
#             SELECT
#                 i.issueid,
#                 i.bookid,
#                 i.memberid,

#                 b.title AS book_title,
#                 m.name AS member_name,

#                 i.issue_date,
#                 i.due_date,
#                 i.return_date,
#                 i.status,

#                 COALESCE(i.fine, 0) AS fine

#             FROM issues i

#             LEFT JOIN books b
#                 ON i.bookid = b.bookid

#             LEFT JOIN members m
#                 ON i.memberid = m.memberid

#             ORDER BY i.issueid DESC

#             LIMIT 10
#         """)

#         recent_issues = cursor.fetchall()

#         # Debug
#         print("Recent Transactions:", recent_issues)

#         # ====================================================
#         # STATS
#         # ====================================================

#         stats = {
#             "total_books": total_books,
#             "available_books": available_books,
#             "total_members": total_members,
#             "issued_books": issued_books,
#             "returned_books": returned_books,
#             "overdue_books": overdue_books,
#             "total_fines": total_fines
#         }

#         # ====================================================
#         # RENDER DASHBOARD
#         # ====================================================

#         return render_template(
#             "dashboard.html",

#             stats=stats,

#             total_books=total_books,
#             available_books=available_books,
#             total_members=total_members,
#             issued_books=issued_books,
#             returned_books=returned_books,
#             overdue_books=overdue_books,
#             total_fines=total_fines,

#             recent_issues=recent_issues
#         )

#     except Exception as e:

#         print(
#             "Dashboard error:",
#             repr(e)
#         )

#         # Empty recent transactions
#         recent_issues = []

#         stats = {
#             "total_books": 0,
#             "available_books": 0,
#             "total_members": 0,
#             "issued_books": 0,
#             "returned_books": 0,
#             "overdue_books": 0,
#             "total_fines": 0
#         }

#         return render_template(
#             "dashboard.html",

#             stats=stats,

#             total_books=0,
#             available_books=0,
#             total_members=0,
#             issued_books=0,
#             returned_books=0,
#             overdue_books=0,
#             total_fines=0,

#             recent_issues=recent_issues
#         )

#     finally:

#         if cursor:
#             cursor.close()

#         if conn:
#             conn.close()


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard", methods=["GET"], endpoint="dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # ====================================================
        # TOTAL BOOKS
        # ====================================================

        cursor.execute("""
            SELECT
                COALESCE(SUM(quantity), 0) AS total
            FROM books
        """)

        total_books = cursor.fetchone()["total"]

        # ====================================================
        # AVAILABLE BOOKS
        # ====================================================

        cursor.execute("""
            SELECT
                COALESCE(SUM(availablequantity), 0) AS total
            FROM books
        """)

        available_books = cursor.fetchone()["total"]

        # ====================================================
        # TOTAL MEMBERS
        # ====================================================

        cursor.execute("""
            SELECT
                COUNT(*) AS total
            FROM members
        """)

        total_members = cursor.fetchone()["total"]

        # ====================================================
        # ISSUED BOOKS
        # ====================================================

        cursor.execute("""
            SELECT
                COUNT(*) AS total
            FROM issues
            WHERE LOWER(status) = 'issued'
        """)

        issued_books = cursor.fetchone()["total"]

        # ====================================================
        # RETURNED BOOKS
        # ====================================================

        cursor.execute("""
            SELECT
                COUNT(*) AS total
            FROM issues
            WHERE LOWER(status) = 'returned'
        """)

        returned_books = cursor.fetchone()["total"]

        # ====================================================
        # OVERDUE BOOKS
        # ====================================================

        cursor.execute("""
            SELECT
                COUNT(*) AS total
            FROM issues
            WHERE LOWER(status) = 'issued'
            AND due_date < CURRENT_DATE
        """)

        overdue_books = cursor.fetchone()["total"]

        # ====================================================
        # TOTAL FINES
        # ====================================================

        cursor.execute("""
            SELECT
                COALESCE(SUM(fine), 0) AS total
            FROM issues
        """)

        total_fines = cursor.fetchone()["total"]

        # ====================================================
        # RECENT TRANSACTIONS
        # ====================================================

        cursor.execute("""
            SELECT
                i.issueid,
                i.bookid,
                i.memberid,

                b.title AS book_title,
                m.name AS member_name,

                COALESCE(i.issue_date, i.issuedate) AS issue_date,
                COALESCE(i.due_date, i.duedate) AS due_date,
                COALESCE(i.return_date, i.returndate) AS return_date,

                i.status,
                COALESCE(i.fine, 0) AS fine

            FROM issues i

            LEFT JOIN books b
                ON i.bookid = b.bookid

            LEFT JOIN members m
                ON i.memberid = m.memberid

            ORDER BY i.issueid DESC

            LIMIT 10
        """)

        recent_issues = cursor.fetchall()

        # ====================================================
        # STATS
        # ====================================================

        stats = {
            "total_books": total_books,
            "available_books": available_books,
            "total_members": total_members,
            "issued_books": issued_books,
            "returned_books": returned_books,
            "overdue_books": overdue_books,
            "total_fines": total_fines
        }

        print("==============================================")
        print("DASHBOARD LOADED")
        print("Total Books:", total_books)
        print("Available Books:", available_books)
        print("Members:", total_members)
        print("Issued:", issued_books)
        print("Returned:", returned_books)
        print("Overdue:", overdue_books)
        print("Fines:", total_fines)
        print("Recent Transactions:", len(recent_issues))
        print("==============================================")

        return render_template(
            "dashboard.html",
            stats=stats,
            total_books=total_books,
            available_books=available_books,
            total_members=total_members,
            issued_books=issued_books,
            returned_books=returned_books,
            overdue_books=overdue_books,
            total_fines=total_fines,
            recent_issues=recent_issues
        )

    except Exception as e:

        print("==============================================")
        print("DASHBOARD ERROR:", repr(e))
        print("==============================================")

        stats = {
            "total_books": 0,
            "available_books": 0,
            "total_members": 0,
            "issued_books": 0,
            "returned_books": 0,
            "overdue_books": 0,
            "total_fines": 0
        }

        return render_template(
            "dashboard.html",
            stats=stats,
            total_books=0,
            available_books=0,
            total_members=0,
            issued_books=0,
            returned_books=0,
            overdue_books=0,
            total_fines=0,
            recent_issues=[]
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()






















# ============================================================
# BOOKS
# ============================================================

@app.route("/books")
def books():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT
                bookid,
                isbn,
                title,
                author,
                category,
                publisher,
                publishyear,
                quantity,
                availablequantity,
                year,
                available,
                created_at
            FROM books
            ORDER BY bookid DESC
        """)

        books_data = cursor.fetchall()

        return render_template(
            "books.html",
            books=books_data
        )

    except Exception as e:

        print(
            "Books error:",
            repr(e)
        )

        flash(
            "Unable to load books: " + str(e),
            "danger"
        )

        return render_template(
            "books.html",
            books=[]
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# ADD BOOK
# ============================================================

@app.route(
    "/books/add",
    methods=["POST"]
)
def add_book():

    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get(
        "title",
        ""
    ).strip()

    author = request.form.get(
        "author",
        ""
    ).strip()

    isbn = request.form.get(
        "isbn",
        ""
    ).strip()

    category = request.form.get(
        "category",
        ""
    ).strip()

    publisher = request.form.get(
        "publisher",
        ""
    ).strip()

    publishyear = request.form.get(
        "publishyear",
        ""
    ).strip()

    if not publishyear:

        publishyear = request.form.get(
            "year",
            ""
        ).strip()

    quantity = request.form.get(
        "quantity",
        "1"
    ).strip()

    if not title:

        flash(
            "Book title is required.",
            "danger"
        )

        return redirect(
            url_for("books")
        )

    if not author:

        flash(
            "Author is required.",
            "danger"
        )

        return redirect(
            url_for("books")
        )

    try:

        quantity = int(quantity)

    except (ValueError, TypeError):

        quantity = 1

    if quantity < 1:
        quantity = 1

    if publishyear:

        try:

            publishyear = int(
                publishyear
            )

        except (
            ValueError,
            TypeError
        ):

            publishyear = None

    else:

        publishyear = None

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO books
            (
                isbn,
                title,
                author,
                category,
                publisher,
                publishyear,
                quantity,
                availablequantity,
                year,
                available
            )
            VALUES
            (
                NULLIF(%s, ''),
                %s,
                %s,
                NULLIF(%s, ''),
                NULLIF(%s, ''),
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING bookid
        """, (
            isbn,
            title,
            author,
            category,
            publisher,
            publishyear,
            quantity,
            quantity,
            publishyear,
            quantity
        ))

        new_book = cursor.fetchone()

        conn.commit()

        print(
            "New book ID:",
            new_book[0]
        )

        flash(
            "Book added successfully.",
            "success"
        )

    except psycopg2.errors.UniqueViolation:

        if conn:
            conn.rollback()

        flash(
            "A book with this ISBN already exists.",
            "danger"
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "Add book error:",
            repr(e)
        )

        flash(
            "Unable to add book: " + str(e),
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

    return redirect(
        url_for("books")
    )


# ============================================================
# DELETE BOOK
# ============================================================

@app.route(
    "/books/delete/<int:book_id>",
    methods=["POST"]
)
def delete_book(book_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM books
            WHERE bookid = %s
        """, (
            book_id,
        ))

        deleted = cursor.rowcount

        conn.commit()

        if deleted:

            flash(
                "Book deleted successfully.",
                "success"
            )

        else:

            flash(
                "Book not found.",
                "danger"
            )

    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "Delete book error:",
            repr(e)
        )

        flash(
            "Unable to delete book: " + str(e),
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

    return redirect(
        url_for("books")
    )


# ============================================================
# MEMBERS
# ============================================================

@app.route("/members")
def members():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""
            SELECT
                memberid,
                name,
                email,
                phone,
                address,
                membership_date,
                status,
                created_at
            FROM members
            ORDER BY memberid DESC
        """)

        members_data = cursor.fetchall()

        return render_template(
            "members.html",
            members=members_data
        )

    except Exception as e:

        print(
            "Members error:",
            repr(e)
        )

        flash(
            "Unable to load members: " + str(e),
            "danger"
        )

        return render_template(
            "members.html",
            members=[]
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# ADD MEMBER
# ============================================================

@app.route(
    "/members/add",
    methods=["POST"]
)
def add_member():

    if "user_id" not in session:
        return redirect(url_for("login"))

    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    address = request.form.get(
        "address",
        ""
    ).strip()

    if not name:

        flash(
            "Member name is required.",
            "danger"
        )

        return redirect(
            url_for("members")
        )

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO members
            (
                name,
                email,
                phone,
                address
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
        """, (
            name,
            email,
            phone,
            address
        ))

        conn.commit()

        flash(
            "Member added successfully.",
            "success"
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "Add member error:",
            repr(e)
        )

        flash(
            "Unable to add member: " + str(e),
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

    return redirect(
        url_for("members")
    )


# ============================================================
# DELETE MEMBER
# ============================================================

@app.route(
    "/members/delete/<int:member_id>",
    methods=["POST"]
)
def delete_member(member_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM members
            WHERE memberid = %s
        """, (
            member_id,
        ))

        deleted = cursor.rowcount

        conn.commit()

        if deleted:

            flash(
                "Member deleted successfully.",
                "success"
            )

        else:

            flash(
                "Member not found.",
                "danger"
            )

    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "Delete member error:",
            repr(e)
        )

        flash(
            "Unable to delete member: " + str(e),
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

    return redirect(
        url_for("members")
    )


# ============================================================
# ISSUE BOOK PAGE
# ============================================================

@app.route("/issue")
def issue_book_page():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # ----------------------------------------------------
        # AVAILABLE BOOKS
        # ----------------------------------------------------
        # IMPORTANT:
        # We calculate available copies from quantity
        # minus currently active issues.
        #
        # This does NOT depend on old/wrong availablequantity
        # values in the database.
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                b.bookid,
                b.title,
                b.author,
                b.quantity,
                (
                    b.quantity -
                    COALESCE(
                        (
                            SELECT COUNT(*)
                            FROM issues i
                            WHERE i.bookid = b.bookid
                            AND i.status = 'Issued'
                        ),
                        0
                    )
                ) AS availablequantity
            FROM books b
            WHERE
                b.quantity -
                COALESCE(
                    (
                        SELECT COUNT(*)
                        FROM issues i
                        WHERE i.bookid = b.bookid
                        AND i.status = 'Issued'
                    ),
                    0
                ) > 0
            ORDER BY b.title ASC
        """)

        books_data = cursor.fetchall()

        # ----------------------------------------------------
        # ACTIVE MEMBERS
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                memberid,
                name,
                email,
                phone
            FROM members
            WHERE status = 'Active'
            ORDER BY name ASC
        """)

        members_data = cursor.fetchall()

        print(
            "Issue page books:",
            len(books_data)
        )

        print(
            "Issue page members:",
            len(members_data)
        )

        return render_template(
            "issue.html",
            books=books_data,
            members=members_data
        )

    except Exception as e:

        print(
            "Issue page error:",
            repr(e)
        )

        flash(
            "Unable to load issue page: " + str(e),
            "danger"
        )

        return render_template(
            "issue.html",
            books=[],
            members=[]
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# ISSUE BOOK
# ============================================================

# @app.route(
#     "/issue/add",
#     methods=["POST"]
# )
# def issue_book():

#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     book_id = request.form.get(
#         "book_id"
#     )

#     member_id = request.form.get(
#         "member_id"
#     )

#     due_date = request.form.get(
#         "due_date"
#     )

#     if not book_id or not member_id:

#         flash(
#             "Please select book and member.",
#             "danger"
#         )

#         return redirect(
#             url_for("issue_book_page")
#         )

#     if not due_date:

#         due_date = (
#             date.today() +
#             timedelta(days=14)
#         )

#     conn = None
#     cursor = None

#     try:

#         conn = get_db_connection()

#         cursor = conn.cursor()

#         # ----------------------------------------------------
#         # LOCK BOOK
#         # ----------------------------------------------------

#         cursor.execute("""
#             SELECT
#                 bookid,
#                 quantity
#             FROM books
#             WHERE bookid = %s
#             FOR UPDATE
#         """, (
#             book_id,
#         ))

#         book = cursor.fetchone()

#         if not book:

#             conn.rollback()

#             flash(
#                 "Book not found.",
#                 "danger"
#             )

#             return redirect(
#                 url_for("issue_book_page")
#             )

#         bookid = book[0]
#         quantity = book[1] or 0

#         # ----------------------------------------------------
#         # COUNT CURRENTLY ISSUED COPIES
#         # ----------------------------------------------------

#         cursor.execute("""
#             SELECT
#                 COUNT(*)
#             FROM issues
#             WHERE bookid = %s
#             AND status = 'Issued'
#         """, (
#             bookid,
#         ))

#         issued_count = cursor.fetchone()[0]

#         # ----------------------------------------------------
#         # CALCULATE AVAILABLE COPIES
#         # ----------------------------------------------------

#         available_count = quantity - issued_count

#         if available_count <= 0:

#             conn.rollback()

#             flash(
#                 "Book is currently unavailable.",
#                 "danger"
#             )

#             return redirect(
#                 url_for("issue_book_page")
#             )

#         # ----------------------------------------------------
#         # CHECK MEMBER
#         # ----------------------------------------------------

#         cursor.execute("""
#             SELECT
#                 memberid
#             FROM members
#             WHERE memberid = %s
#             AND status = 'Active'
#         """, (
#             member_id,
#         ))

#         member = cursor.fetchone()

#         if not member:

#             conn.rollback()

#             flash(
#                 "Selected member is not active or does not exist.",
#                 "danger"
#             )

#             return redirect(
#                 url_for("issue_book_page")
#             )

#         # ----------------------------------------------------
#         # INSERT ISSUE
#         # ----------------------------------------------------

#         cursor.execute("""
#             INSERT INTO issues
#             (
#                 bookid,
#                 memberid,
#                 issue_date,
#                 due_date,
#                 status
#             )
#             VALUES
#             (
#                 %s,
#                 %s,
#                 CURRENT_DATE,
#                 %s,
#                 'Issued'
#             )
#         """, (
#             bookid,
#             member_id,
#             due_date
#         ))

#         # ----------------------------------------------------
#         # UPDATE BOOK AVAILABILITY
#         # ----------------------------------------------------

#         new_available = available_count - 1

#         cursor.execute("""
#             UPDATE books
#             SET
#                 availablequantity = %s,
#                 available = %s
#             WHERE bookid = %s
#         """, (
#             new_available,
#             new_available,
#             bookid
#         ))

#         conn.commit()

#         flash(
#             "Book issued successfully.",
#             "success"
#         )

#     except Exception as e:

#         if conn:
#             conn.rollback()

#         print(
#             "Issue book error:",
#             repr(e)
#         )

#         flash(
#             "Unable to issue book: " + str(e),
#             "danger"
#         )

#     finally:

#         if cursor:
#             cursor.close()

#         if conn:
#             conn.close()

#     return redirect(
#         url_for("issue_book_page")
#     )



# ============================================================
# ISSUE BOOK
# ============================================================

@app.route("/issue/add", methods=["POST"])
def issue_book():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # --------------------------------------------------------
    # GET FORM DATA
    # --------------------------------------------------------

    book_id = request.form.get("book_id", "").strip()
    member_id = request.form.get("member_id", "").strip()
    issue_date_str = request.form.get("issue_date", "").strip()
    due_date_str = request.form.get("due_date", "").strip()

    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    if not book_id or not member_id:
        flash(
            "Please select book and member.",
            "danger"
        )
        return redirect(url_for("issue_book_page"))

    # --------------------------------------------------------
    # DATE VALIDATION
    # --------------------------------------------------------

    try:

        if issue_date_str:
            issue_date = date.fromisoformat(issue_date_str)
        else:
            issue_date = date.today()

        if due_date_str:
            due_date = date.fromisoformat(due_date_str)
        else:
            due_date = issue_date + timedelta(days=14)

    except ValueError:

        flash(
            "Invalid issue or due date.",
            "danger"
        )

        return redirect(
            url_for("issue_book_page")
        )

    # --------------------------------------------------------
    # DUE DATE CHECK
    # --------------------------------------------------------

    if due_date < issue_date:

        flash(
            "Due date cannot be before issue date.",
            "danger"
        )

        return redirect(
            url_for("issue_book_page")
        )

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor()

        # ====================================================
        # LOCK BOOK
        # ====================================================

        cursor.execute("""
            SELECT
                bookid,
                quantity,
                availablequantity
            FROM books
            WHERE bookid = %s
            FOR UPDATE
        """, (
            book_id,
        ))

        book = cursor.fetchone()

        if not book:

            conn.rollback()

            flash(
                "Book not found.",
                "danger"
            )

            return redirect(
                url_for("issue_book_page")
            )

        bookid = book[0]
        quantity = book[1] or 0
        available_quantity = book[2]

        # ----------------------------------------------------
        # SAFETY: RECALCULATE REAL AVAILABLE COPIES
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM issues
            WHERE bookid = %s
            AND status = 'Issued'
        """, (
            bookid,
        ))

        issued_count = cursor.fetchone()[0]

        real_available = max(
            quantity - issued_count,
            0
        )

        # ----------------------------------------------------
        # CHECK AVAILABILITY
        # ----------------------------------------------------

        if real_available <= 0:

            conn.rollback()

            flash(
                "Book is currently unavailable.",
                "danger"
            )

            return redirect(
                url_for("issue_book_page")
            )

        # ====================================================
        # CHECK MEMBER
        # ====================================================

        cursor.execute("""
            SELECT
                memberid,
                status
            FROM members
            WHERE memberid = %s
        """, (
            member_id,
        ))

        member = cursor.fetchone()

        if not member:

            conn.rollback()

            flash(
                "Member not found.",
                "danger"
            )

            return redirect(
                url_for("issue_book_page")
            )

        if member[1] != "Active":

            conn.rollback()

            flash(
                "Selected member is not active.",
                "danger"
            )

            return redirect(
                url_for("issue_book_page")
            )

        # ====================================================
        # INSERT ISSUE
        #
        # Your database currently has BOTH:
        #
        # issuedate
        # duedate
        # returndate
        #
        # AND:
        #
        # issue_date
        # due_date
        # return_date
        #
        # So we fill the old + new columns.
        # ====================================================

        cursor.execute("""
            INSERT INTO issues
            (
                bookid,
                memberid,

                issuedate,
                duedate,
                returndate,

                issue_date,
                due_date,
                return_date,

                fine,
                status
            )

            VALUES
            (
                %s,
                %s,

                %s,
                %s,
                NULL,

                %s,
                %s,
                NULL,

                0,
                'Issued'
            )

            RETURNING issueid
        """, (
            bookid,
            member_id,

            issue_date,
            due_date,

            issue_date,
            due_date
        ))

        new_issue = cursor.fetchone()

        # ====================================================
        # UPDATE BOOK AVAILABILITY
        # ====================================================

        new_available = max(
            real_available - 1,
            0
        )

        cursor.execute("""
            UPDATE books
            SET
                availablequantity = %s,
                available = %s
            WHERE bookid = %s
        """, (
            new_available,
            new_available,
            bookid
        ))

        # ====================================================
        # COMMIT
        # ====================================================

        conn.commit()

        print(
            "=============================================="
        )

        print(
            "BOOK ISSUED SUCCESSFULLY"
        )

        print(
            "Issue ID:",
            new_issue[0]
        )

        print(
            "Book ID:",
            bookid
        )

        print(
            "Member ID:",
            member_id
        )

        print(
            "Issue Date:",
            issue_date
        )

        print(
            "Due Date:",
            due_date
        )

        print(
            "Available Copies:",
            new_available
        )

        print(
            "=============================================="
        )

        flash(
            "Book issued successfully.",
            "success"
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "=============================================="
        )

        print(
            "ISSUE BOOK ERROR:",
            repr(e)
        )

        print(
            "=============================================="
        )

        flash(
            "Unable to issue book: " + str(e),
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

    return redirect(
        url_for("issue_book_page")
    )




















































# # ============================================================
# # RETURN BOOK PAGE
# # ============================================================

# @app.route("/return")
# def return_book_page():

#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     conn = None
#     cursor = None

#     try:

#         conn = get_db_connection()

#         cursor = conn.cursor(
#             cursor_factory=RealDictCursor
#         )

#         cursor.execute("""
#             SELECT
#                 i.issueid,
#                 i.bookid,
#                 i.memberid,
#                 b.title,
#                 m.name AS member_name,
#                 i.issue_date,
#                 i.due_date,
#                 i.status,
#                 i.fine
#             FROM issues i
#             INNER JOIN books b
#                 ON i.bookid = b.bookid
#             INNER JOIN members m
#                 ON i.memberid = m.memberid
#             WHERE i.status = 'Issued'
#             ORDER BY i.issueid DESC
#         """)

#         active_issues = cursor.fetchall()

#         return render_template(
#             "return.html",
#             active_issues=active_issues
#         )

#     except Exception as e:

#         print(
#             "Return page error:",
#             repr(e)
#         )

#         flash(
#             "Unable to load return page: " + str(e),
#             "danger"
#         )

#         return render_template(
#             "return.html",
#             active_issues=[]
#         )

#     finally:

#         if cursor:
#             cursor.close()

#         if conn:
#             conn.close()


# # ============================================================
# # RETURN BOOK
# # ============================================================

# @app.route(
#     "/return/add",
#     methods=["POST"]
# )
# def return_book():

#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     issue_id = request.form.get(
#         "issue_id"
#     )

#     if not issue_id:

#         flash(
#             "Please select an issue record.",
#             "danger"
#         )

#         return redirect(
#             url_for("return_book_page")
#         )

#     conn = None
#     cursor = None

#     try:

#         conn = get_db_connection()

#         cursor = conn.cursor(
#             cursor_factory=RealDictCursor
#         )

#         # GET ISSUE

#         cursor.execute("""
#             SELECT
#                 issueid,
#                 bookid,
#                 due_date
#             FROM issues
#             WHERE issueid = %s
#             AND status = 'Issued'
#             FOR UPDATE
#         """, (
#             issue_id,
#         ))

#         issue = cursor.fetchone()

#         if not issue:

#             conn.rollback()

#             flash(
#                 "Active issue record not found.",
#                 "danger"
#             )

#             return redirect(
#                 url_for("return_book_page")
#             )

#         # CALCULATE FINE

#         fine = 0

#         if issue["due_date"]:

#             overdue_days = (
#                 date.today() -
#                 issue["due_date"]
#             ).days

#             if overdue_days > 0:

#                 fine = overdue_days * 10

#         # UPDATE ISSUE

#         cursor.execute("""
#             UPDATE issues
#             SET
#                 return_date = CURRENT_DATE,
#                 status = 'Returned',
#                 fine = %s
#             WHERE issueid = %s
#         """, (
#             fine,
#             issue_id
#         ))

#         # ----------------------------------------------------
#         # RECALCULATE BOOK AVAILABILITY
#         # ----------------------------------------------------

#         cursor.execute("""
#             SELECT
#                 quantity
#             FROM books
#             WHERE bookid = %s
#             FOR UPDATE
#         """, (
#             issue["bookid"],
#         ))

#         book = cursor.fetchone()

#         if book:

#             quantity = book["quantity"] or 0

#             cursor.execute("""
#                 SELECT
#                     COUNT(*)
#                 FROM issues
#                 WHERE bookid = %s
#                 AND status = 'Issued'
#             """, (
#                 issue["bookid"],
#             ))

#             issued_count = cursor.fetchone()[0]

#             new_available = max(
#                 quantity - issued_count,
#                 0
#             )

#             cursor.execute("""
#                 UPDATE books
#                 SET
#                     availablequantity = %s,
#                     available = %s
#                 WHERE bookid = %s
#             """, (
#                 new_available,
#                 new_available,
#                 issue["bookid"]
#             ))

#         conn.commit()

#         if fine > 0:

#             flash(
#                 f"Book returned successfully. Fine: Rs. {fine}",
#                 "success"
#             )

#         else:

#             flash(
#                 "Book returned successfully.",
#                 "success"
#             )

#     except Exception as e:

#         if conn:
#             conn.rollback()

#         print(
#             "Return book error:",
#             repr(e)
#         )

#         flash(
#             "Unable to return book: " + str(e),
#             "danger"
#         )

#     finally:

#         if cursor:
#             cursor.close()

#         if conn:
#             conn.close()

#     return redirect(
#         url_for("return_book_page")
#     )



# # ============================================================
# # RETURN BOOK PAGE
# # ============================================================

# @app.route("/return")
# def return_book_page():

#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     conn = None
#     cursor = None

#     try:

#         conn = get_db_connection()

#         cursor = conn.cursor(
#             cursor_factory=RealDictCursor
#         )

#         cursor.execute("""
#             SELECT
#                 i.issueid,
#                 i.bookid,
#                 i.memberid,

#                 b.title,
#                 b.author,

#                 m.name AS member_name,
#                 m.email AS member_email,

#                 COALESCE(i.issue_date, i.issuedate) AS issue_date,
#                 COALESCE(i.due_date, i.duedate) AS due_date,

#                 i.status,
#                 COALESCE(i.fine, 0) AS fine

#             FROM issues i

#             INNER JOIN books b
#                 ON i.bookid = b.bookid

#             INNER JOIN members m
#                 ON i.memberid = m.memberid

#             WHERE LOWER(COALESCE(i.status, 'issued')) = 'issued'

#             ORDER BY i.issueid DESC
#         """)

#         active_issues = cursor.fetchall()

#         print("ACTIVE ISSUES:", active_issues)

#         return render_template(
#             "return.html",
#             active_issues=active_issues
#         )

#     except Exception as e:

#         print(
#             "Return page error:",
#             repr(e)
#         )

#         if conn:
#             conn.rollback()

#         flash(
#             "Unable to load return page: " + str(e),
#             "danger"
#         )

#         return render_template(
#             "return.html",
#             active_issues=[]
#         )

#     finally:

#         if cursor:
#             cursor.close()

#         if conn:
#             conn.close()


# # ============================================================
# # RETURN BOOK
# # ============================================================

# # @app.route(
# #     "/return/add",
# #     methods=["POST"]
# # )
# # def return_book():

# #     if "user_id" not in session:
# #         return redirect(url_for("login"))

# #     issue_id = request.form.get("issue_id")

# #     if not issue_id:

# #         flash(
# #             "Please select an issue record.",
# #             "danger"
# #         )

# #         return redirect(
# #             url_for("return_book_page")
# #         )

# #     conn = None
# #     cursor = None

# #     try:

# #         conn = get_db_connection()

# #         cursor = conn.cursor(
# #             cursor_factory=RealDictCursor
# #         )

# #         # ====================================================
# #         # GET ACTIVE ISSUE
# #         # ====================================================

# #         cursor.execute("""
# #             SELECT
# #                 issueid,
# #                 bookid,
# #                 memberid,

# #                 COALESCE(due_date, duedate) AS due_date,

# #                 status

# #             FROM issues

# #             WHERE issueid = %s

# #             AND LOWER(COALESCE(status, 'issued')) = 'issued'

# #             FOR UPDATE
# #         """, (
# #             issue_id,
# #         ))

# #         issue = cursor.fetchone()

# #         if not issue:

# #             conn.rollback()

# #             flash(
# #                 "Active issue record not found.",
# #                 "danger"
# #             )

# #             return redirect(
# #                 url_for("return_book_page")
# #             )

# #         # ====================================================
# #         # CALCULATE FINE
# #         # ====================================================

# #         fine = 0

# #         if issue["due_date"]:

# #             overdue_days = (
# #                 date.today() -
# #                 issue["due_date"]
# #             ).days

# #             if overdue_days > 0:

# #                 fine = overdue_days * 10

# #         # ====================================================
# #         # UPDATE ISSUE
# #         # ====================================================

# #         cursor.execute("""
# #             UPDATE issues

# #             SET
# #                 return_date = CURRENT_DATE,
# #                 returndate = CURRENT_DATE,

# #                 status = 'Returned',

# #                 fine = %s

# #             WHERE issueid = %s
# #         """, (
# #             fine,
# #             issue_id
# #         ))

# #         # ====================================================
# #         # RECALCULATE BOOK AVAILABILITY
# #         # ====================================================

# #         cursor.execute("""
# #             SELECT
# #                 quantity
# #             FROM books
# #             WHERE bookid = %s
# #             FOR UPDATE
# #         """, (
# #             issue["bookid"],
# #         ))

# #         book = cursor.fetchone()

# #         if book:

# #             quantity = book["quantity"] or 0

# #             cursor.execute("""
# #                 SELECT COUNT(*) AS issued_count

# #                 FROM issues

# #                 WHERE bookid = %s

# #                 AND LOWER(COALESCE(status, 'issued')) = 'issued'
# #             """, (
# #                 issue["bookid"],
# #             ))

# #             result = cursor.fetchone()

# #             issued_count = result["issued_count"] or 0

# #             new_available = max(
# #                 quantity - issued_count,
# #                 0
# #             )

# #             cursor.execute("""
# #                 UPDATE books

# #                 SET
# #                     availablequantity = %s,
# #                     available = %s

# #                 WHERE bookid = %s
# #             """, (
# #                 new_available,
# #                 new_available,
# #                 issue["bookid"]
# #             ))

# #         # ====================================================
# #         # COMMIT
# #         # ====================================================

# #         conn.commit()

# #         if fine > 0:

# #             flash(
# #                 f"Book returned successfully. Fine: Rs. {fine}",
# #                 "success"
# #             )

# #         else:

# #             flash(
# #                 "Book returned successfully.",
# #                 "success"
# #             )

# #     except Exception as e:

# #         if conn:
# #             conn.rollback()

# #         print(
# #             "Return book error:",
# #             repr(e)
# #         )

# #         flash(
# #             "Unable to return book: " + str(e),
# #             "danger"
# #         )

# #     finally:

# #         if cursor:
# #             cursor.close()

# #         if conn:
# #             conn.close()

# #     return redirect(
# #         url_for("return_book_page")
# #     )




# # ============================================================
# # RETURN BOOK
# # ============================================================

# @app.route("/return/add", methods=["POST"])
# def return_book():

#     if "user_id" not in session:
#         return redirect(url_for("login"))

#     issue_id = request.form.get("issue_id")
#     return_date = request.form.get("return_date")

#     if not issue_id:
#         flash("Issue record was not selected.", "danger")
#         return redirect(url_for("return_book_page"))

#     if not return_date:
#         return_date = date.today()

#     conn = None
#     cursor = None

#     try:

#         conn = get_db_connection()

#         cursor = conn.cursor(
#             cursor_factory=RealDictCursor
#         )

#         # ----------------------------------------------------
#         # GET ACTIVE ISSUE
#         # ----------------------------------------------------

#         cursor.execute("""
#             SELECT
#                 i.issueid,
#                 i.bookid,
#                 i.memberid,
#                 i.due_date,
#                 b.title,
#                 b.quantity
#             FROM issues i
#             INNER JOIN books b
#                 ON i.bookid = b.bookid
#             WHERE i.issueid = %s
#               AND i.status = 'Issued'
#             FOR UPDATE
#         """, (issue_id,))

#         issue = cursor.fetchone()

#         if not issue:

#             conn.rollback()

#             flash(
#                 "Active issued book record was not found.",
#                 "danger"
#             )

#             return redirect(
#                 url_for("return_book_page")
#             )

#         # ----------------------------------------------------
#         # CALCULATE FINE
#         # ----------------------------------------------------

#         fine = 0

#         if issue["due_date"]:

#             if isinstance(return_date, str):
#                 return_date_obj = datetime.strptime(
#                     return_date,
#                     "%Y-%m-%d"
#                 ).date()
#             else:
#                 return_date_obj = return_date

#             overdue_days = (
#                 return_date_obj -
#                 issue["due_date"]
#             ).days

#             if overdue_days > 0:

#                 fine = overdue_days * 50

#         # ----------------------------------------------------
#         # UPDATE ISSUE
#         # ----------------------------------------------------

#         cursor.execute("""
#             UPDATE issues
#             SET
#                 return_date = %s,
#                 status = 'Returned',
#                 fine = %s
#             WHERE issueid = %s
#         """, (
#             return_date,
#             fine,
#             issue_id
#         ))

#         # ----------------------------------------------------
#         # RECALCULATE AVAILABLE BOOKS
#         # ----------------------------------------------------

#         cursor.execute("""
#             SELECT
#                 quantity
#             FROM books
#             WHERE bookid = %s
#             FOR UPDATE
#         """, (
#             issue["bookid"],
#         ))

#         book = cursor.fetchone()

#         if book:

#             quantity = book["quantity"] or 0

#             cursor.execute("""
#                 SELECT COUNT(*) AS issued_count
#                 FROM issues
#                 WHERE bookid = %s
#                   AND status = 'Issued'
#             """, (
#                 issue["bookid"],
#             ))

#             result = cursor.fetchone()

#             issued_count = result["issued_count"] or 0

#             available_quantity = max(
#                 quantity - issued_count,
#                 0
#             )

#             cursor.execute("""
#                 UPDATE books
#                 SET
#                     availablequantity = %s,
#                     available = %s
#                 WHERE bookid = %s
#             """, (
#                 available_quantity,
#                 available_quantity,
#                 issue["bookid"]
#             ))

#         # ----------------------------------------------------
#         # COMMIT
#         # ----------------------------------------------------

#         conn.commit()

#         if fine > 0:

#             flash(
#                 f"Book returned successfully. Fine: Rs. {fine}",
#                 "success"
#             )

#         else:

#             flash(
#                 "Book returned successfully.",
#                 "success"
#             )

#     except Exception as e:

#         if conn:
#             conn.rollback()

#         print(
#             "RETURN BOOK ERROR:",
#             repr(e)
#         )

#         flash(
#             "Unable to return book: " + str(e),
#             "danger"
#         )

#     finally:

#         if cursor:
#             cursor.close()

#         if conn:
#             conn.close()

#     return redirect(
#         url_for("return_book_page")
#     )



# ============================================================
# RETURN BOOK PAGE
# ============================================================

@app.route("/return")
def return_book_page():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:
        conn = get_db_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # ----------------------------------------------------
        # GET ALL CURRENTLY ISSUED BOOKS
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                i.issueid,
                i.bookid,
                i.memberid,
                i.issue_date,
                i.due_date,
                i.status,
                i.fine,

                b.title,
                b.author,

                m.name AS member_name

            FROM issues i

            INNER JOIN books b
                ON i.bookid = b.bookid

            INNER JOIN members m
                ON i.memberid = m.memberid

            WHERE LOWER(i.status) = 'issued'

            ORDER BY i.issueid DESC
        """)

        issued_books = cursor.fetchall()

        return render_template(
            "return.html",
            issued_books=issued_books
        )

    except Exception as e:

        print(
            "RETURN PAGE ERROR:",
            repr(e)
        )

        if conn:
            conn.rollback()

        flash(
            "Unable to load return books: " + str(e),
            "danger"
        )

        return render_template(
            "return.html",
            issued_books=[]
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# RETURN BOOK
# ============================================================

@app.route(
    "/return/add",
    methods=["POST"]
)
def return_book():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # --------------------------------------------------------
    # IMPORTANT:
    # return.html sends:
    # name="issue_id"
    # --------------------------------------------------------

    issue_id = request.form.get("issue_id")

    return_date = request.form.get("return_date")

    print("========================================")
    print("RETURN BOOK REQUEST")
    print("Issue ID:", issue_id)
    print("Return Date:", return_date)
    print("========================================")

    if not issue_id:

        flash(
            "Please select an issue record.",
            "danger"
        )

        return redirect(
            url_for("return_book_page")
        )

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # ====================================================
        # GET ACTIVE ISSUE
        # ====================================================

        cursor.execute("""
            SELECT
                issueid,
                bookid,
                memberid,
                issue_date,
                due_date,
                status

            FROM issues

            WHERE issueid = %s
            AND LOWER(status) = 'issued'

            FOR UPDATE
        """, (
            issue_id,
        ))

        issue = cursor.fetchone()

        print("ISSUE FOUND:", issue)

        if not issue:

            conn.rollback()

            flash(
                "Active issue record not found.",
                "danger"
            )

            return redirect(
                url_for("return_book_page")
            )

        # ====================================================
        # CALCULATE FINE
        # ====================================================

        fine = 0

        if issue["due_date"]:

            # Use selected return date if provided
            if return_date:

                try:

                    actual_return_date = datetime.strptime(
                        return_date,
                        "%Y-%m-%d"
                    ).date()

                except ValueError:

                    actual_return_date = date.today()

            else:

                actual_return_date = date.today()

            overdue_days = (
                actual_return_date -
                issue["due_date"]
            ).days

            if overdue_days > 0:

                # Rs. 50 per overdue day
                fine = overdue_days * 50

        print("CALCULATED FINE:", fine)

        # ====================================================
        # UPDATE ISSUE RECORD
        # ====================================================

        cursor.execute("""
            UPDATE issues

            SET
                return_date = %s,
                status = 'Returned',
                fine = %s

            WHERE issueid = %s
        """, (
            actual_return_date,
            fine,
            issue_id
        ))

        print(
            "ISSUE UPDATED:",
            cursor.rowcount
        )

        # ====================================================
        # RECALCULATE BOOK AVAILABILITY
        # ====================================================

        cursor.execute("""
            SELECT
                quantity
            FROM books

            WHERE bookid = %s

            FOR UPDATE
        """, (
            issue["bookid"],
        ))

        book = cursor.fetchone()

        print("BOOK:", book)

        if book:

            quantity = book["quantity"] or 0

            # ------------------------------------------------
            # COUNT CURRENTLY ISSUED COPIES
            # ------------------------------------------------

            cursor.execute("""
                SELECT
                    COUNT(*) AS issued_count

                FROM issues

                WHERE bookid = %s
                AND LOWER(status) = 'issued'
            """, (
                issue["bookid"],
            ))

            issued_result = cursor.fetchone()

            issued_count = (
                issued_result["issued_count"]
                if issued_result
                else 0
            )

            # ------------------------------------------------
            # AVAILABLE = TOTAL - ISSUED
            # ------------------------------------------------

            new_available = max(
                quantity - issued_count,
                0
            )

            print(
                "TOTAL QUANTITY:",
                quantity
            )

            print(
                "ISSUED COUNT:",
                issued_count
            )

            print(
                "NEW AVAILABLE:",
                new_available
            )

            # ------------------------------------------------
            # UPDATE BOOK
            # ------------------------------------------------

            cursor.execute("""
                UPDATE books

                SET
                    availablequantity = %s,
                    available = %s

                WHERE bookid = %s
            """, (
                new_available,
                new_available,
                issue["bookid"]
            ))

            print(
                "BOOK UPDATED:",
                cursor.rowcount
            )

        # ====================================================
        # COMMIT EVERYTHING
        # ====================================================

        conn.commit()

        print("RETURN TRANSACTION COMMITTED SUCCESSFULLY")

        # ====================================================
        # SUCCESS MESSAGE
        # ====================================================

        if fine > 0:

            flash(
                f"Book returned successfully. Fine: Rs. {fine}",
                "success"
            )

        else:

            flash(
                "Book returned successfully.",
                "success"
            )

    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "========================================"
        )

        print(
            "RETURN BOOK ERROR:",
            repr(e)
        )

        print(
            "========================================"
        )

        flash(
            "Unable to return book: " + str(e),
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

    return redirect(
        url_for("return_book_page")
    )

























































































# ============================================================
# REPORTS
# ============================================================

@app.route("/reports")
def reports():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor(
            cursor_factory=RealDictCursor
        )

        # TOTAL BOOKS

        cursor.execute("""
            SELECT
                COALESCE(SUM(quantity), 0) AS total
            FROM books
        """)

        total_books = cursor.fetchone()["total"]

        # TOTAL MEMBERS

        cursor.execute("""
            SELECT
                COUNT(*) AS total
            FROM members
        """)

        total_members = cursor.fetchone()["total"]

        # ISSUED BOOKS

        cursor.execute("""
            SELECT
                COUNT(*) AS total
            FROM issues
            WHERE status = 'Issued'
        """)

        issued_books = cursor.fetchone()["total"]

        # RETURNED BOOKS

        cursor.execute("""
            SELECT
                COUNT(*) AS total
            FROM issues
            WHERE status = 'Returned'
        """)

        returned_books = cursor.fetchone()["total"]

        # OVERDUE BOOKS

        cursor.execute("""
            SELECT
                COUNT(*) AS total
            FROM issues
            WHERE status = 'Issued'
            AND due_date < CURRENT_DATE
        """)

        overdue_books = cursor.fetchone()["total"]

        # TOTAL FINES

        cursor.execute("""
            SELECT
                COALESCE(SUM(fine), 0) AS total
            FROM issues
        """)

        total_fines = cursor.fetchone()["total"]

        # RECENT ACTIVITY

        cursor.execute("""
            SELECT
                i.issueid,
                b.title,
                m.name AS member_name,
                i.issue_date,
                i.due_date,
                i.return_date,
                i.status,
                i.fine
            FROM issues i
            INNER JOIN books b
                ON i.bookid = b.bookid
            INNER JOIN members m
                ON i.memberid = m.memberid
            ORDER BY i.issueid DESC
            LIMIT 20
        """)

        recent_activity = cursor.fetchall()

        return render_template(
            "reports.html",
            total_books=total_books,
            total_members=total_members,
            issued_books=issued_books,
            returned_books=returned_books,
            overdue_books=overdue_books,
            total_fines=total_fines,
            recent_activity=recent_activity
        )

    except Exception as e:

        print(
            "Reports error:",
            repr(e)
        )

        return render_template(
            "reports.html",
            total_books=0,
            total_members=0,
            issued_books=0,
            returned_books=0,
            overdue_books=0,
            total_fines=0,
            recent_activity=[]
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# ERROR HANDLER
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <div style="
        font-family: Arial;
        padding: 50px;
        text-align: center;
    ">
        <h1>404</h1>
        <p>Page not found.</p>
        <a href="/">Back to Login</a>
    </div>
    """, 404
















# ============================================================
# DEBUG ROUTES
# ============================================================

print()
print("REGISTERED FLASK ROUTES")
print("=" * 60)

for rule in app.url_map.iter_rules():
    print(
        rule.endpoint,
        "=>",
        rule.rule,
        list(rule.methods)
    )

print("=" * 60)





# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 55)
    print("             LIBRARYPRO")
    print("       Library Management System")
    print("=" * 55)
    print()

    print(
        "Initializing PostgreSQL database..."
    )

    init_database()

    print()
    print(
        "Starting Flask server..."
    )

    print()
    print(
        "Local URL:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()
    print("=" * 55)
    print()

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        ),
        debug=True
    )