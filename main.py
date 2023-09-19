from datetime import datetime

from flask import Flask, request, jsonify
import mysql.connector
import requests

app = Flask(__name__)

# MySQL Configuration
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Admin@123",
    database="interview"
)

cursor = db.cursor()


@app.route('/add_book', methods=['POST'])
def add_book():
    data = request.json
    title = data['title']
    author = data['author']

    # Insert the book into the MySQL database
    query = "INSERT INTO books (title, author) VALUES (%s, %s)"
    values = (title, author)
    cursor.execute(query, values)
    db.commit()

    return "Book added successfully"


@app.route('/get_book/<int:book_id>', methods=['GET'])
def get_book(book_id):
    query = "SELECT * FROM books WHERE id = %s AND active_flag = %s"
    values = (book_id, 1)
    cursor.execute(query, values)
    book = cursor.fetchone()

    if book:
        book_data = {
            "title": book[1],
            "author": book[2],
        }
        return jsonify(book_data)
    else:
        return "Book not found", 404


@app.route('/update_book/<int:book_id>', methods=['PUT'])
def edit_book(book_id):
    data = request.json
    title = data['title']
    author = data['author']

    query = "UPDATE books SET title = %s, author = %s WHERE id = %s"
    values = (title, author, book_id)
    cursor.execute(query, values)
    db.commit()

    return "Book updated successfully"


@app.route('/delete_book/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):

    query = "UPDATE books SET active_flag = %s WHERE id = %s"
    cursor.execute(query, (0, book_id))
    db.commit()
    return "Book deleted successfully"


@app.route('/add_member', methods=['POST'])
def add_member():
    data = request.json
    name = data['name']
    email = data['email']

    query = "INSERT INTO members (name, email) VALUES (%s, %s)"
    values = (name, email)
    cursor.execute(query, values)
    db.commit()

    return "Member added successfully"


@app.route('/get_member/<int:member_id>', methods=['GET'])
def get_member(member_id):
    query = "SELECT * FROM members WHERE id = %s AND active_flag = %s"
    values = (member_id, 1)
    cursor.execute(query, values)
    member = cursor.fetchone()

    if member:
        member_data = {
            "name": member[1],
            "email": member[2]
        }
        return jsonify(member_data)
    else:
        return "Member not found", 404


@app.route('/update_member/<int:member_id>', methods=['PUT'])
def edit_member(member_id):
    data = request.json
    name = data['name']
    email = data['email']

    query = "UPDATE members SET name = %s, email = %s WHERE id = %s"
    values = (name, email, member_id)
    cursor.execute(query, values)
    db.commit()

    return "Member updated successfully"


@app.route('/delete_member/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    query = "UPDATE members SET active_flag=%s WHERE id = %s"
    cursor.execute(query, (0, member_id))
    db.commit()
    return "Member deleted successfully"


@app.route('/issue_book', methods=['POST'])
def issue_book():
    data = request.json
    member_id = data['member_id']
    book_id = data['book_id']
    issue_date = data['issue_date']
    due_date = data['due_date']

    member_query = "SELECT * FROM members WHERE id = %s AND active_flag = %s"
    member_values = (member_id, 1)
    cursor.execute(member_query, member_values)
    member = cursor.fetchone()

    book_query = "SELECT * FROM books WHERE id = %s AND active_flag = %s"
    book_values = (book_id, 1)
    cursor.execute(book_query, book_values)
    book = cursor.fetchone()

    if member and book:
        transaction_query = ("INSERT INTO transactions "
                             "(member_id, book_id, issue_date, due_date) "
                             "VALUES (%s, %s, %s, %s)")
        transaction_values = (member_id, book_id, issue_date, due_date)
        cursor.execute(transaction_query, transaction_values)
        db.commit()

        update_book_query = "UPDATE books SET availability = %s WHERE id = %s"
        update_book_values = ("issued", book_id)
        cursor.execute(update_book_query, update_book_values)
        db.commit()

        return "Book issued successfully"
    else:
        return "Member or book not found", 404


@app.route('/return_book', methods=['POST'])
def return_book():
    data = request.json
    member_id = data['member_id']
    book_id = data['book_id']
    return_date = data['return_date']

    member_query = "SELECT * FROM members WHERE id = %s AND active_flag = %s"
    member_values = (member_id, 1)
    cursor.execute(member_query, member_values)
    member = cursor.fetchone()

    book_query = "SELECT * FROM books WHERE id = %s AND active_flag = %s"
    book_values = (book_id, 1)
    cursor.execute(book_query, book_values)
    book = cursor.fetchone()

    if member and book:
        transaction_query = ("SELECT * FROM transactions WHERE member_id = %s "
                             "AND book_id = %s AND return_date IS NULL")
        transaction_values = (member_id, book_id)
        cursor.execute(transaction_query, transaction_values)
        transaction = cursor.fetchone()

        if transaction:
            due_date = transaction[4]
            return_date = datetime.strptime(return_date, "%Y-%m-%d %H:%M:%S")
            if return_date > due_date:
                late_fee = calculate_late_fee(return_date, due_date)  # Implement this function
            else:
                late_fee = 0

            update_transaction_query = "UPDATE transactions SET return_date = %s, late_fee = %s WHERE id = %s"
            update_transaction_values = (return_date, late_fee, transaction[0])
            cursor.execute(update_transaction_query, update_transaction_values)
            db.commit()

            update_book_query = "UPDATE books SET availability = %s WHERE id = %s"
            update_book_values = ("available", book_id)
            cursor.execute(update_book_query, update_book_values)
            db.commit()

            return "Book returned successfully with late fee: Rs. {}".format(late_fee)
        else:
            return "Book was not issued to this member", 404
    else:
        return "Member or book not found", 404


def calculate_late_fee(return_date, due_date):
    try:
        LATE_FEE_RATE_PER_DAY = 5
        # return_date = datetime.strptime(return_date, "%Y-%m-%d")
        # due_date = datetime.strptime(due_date, "%Y-%m-%d")

        days_late = (return_date - due_date).days

        late_fee = max(0, days_late * LATE_FEE_RATE_PER_DAY)
        return late_fee
    except Exception as e:
        print(f"Error calculating late fee: {str(e)}")
        return 0


@app.route('/search_books', methods=['POST'])
def search_books():
    data = request.json
    search_title = data.get('title', '')
    search_author = data.get('author', '')

    query = "SELECT * FROM books WHERE title LIKE %s AND author LIKE %s AND active_flag=%s"
    values = (f'%{search_title}%', f'%{search_author}%', 1)
    cursor.execute(query, values)
    books = cursor.fetchall()

    book_list = []
    for book in books:
        book_data = {
            "title": book[1],
            "author": book[2]
        }
        book_list.append(book_data)

    return jsonify(book_list)


FRAPPE_API_URL = "https://frappe.io/api/method/frappe-library"


@app.route('/import_books', methods=['POST'])
def import_books():
    data = request.json
    num_books_to_import = int(data['num_books'])
    title_to_import = data.get('title', '')

    params = {
        "page": 1,
        "title": title_to_import,
    }

    imported_books = []

    for num in range(num_books_to_import):
        response = requests.get(FRAPPE_API_URL, params=params)
        data = response.json().get("message", [])

        if not data:
            break

        for book_data in data:
            title = book_data.get("title", "")
            author = book_data.get("authors", "")
            isbn = book_data.get("isbn", "")
            publisher = book_data.get("publisher", "")
            page = book_data.get("num_pages", "")

            # Insert the book into the database
            insert_query = "INSERT INTO books (title, author, isbn, publisher) VALUES (%s, %s, %s, %s)"
            insert_values = (title, author, isbn, publisher)
            cursor.execute(insert_query, insert_values)
            db.commit()

            imported_books.append({
                "title": title,
                "author": author,
                "isbn": isbn,
                "publisher": publisher,
                # "page": page
            })

        imported_books.extend(data)

        params["page"] += 1

    return jsonify(imported_books)


if __name__ == '__main__':
    app.run(debug=True)
