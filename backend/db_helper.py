
import os
import mysql.connector
from contextlib import contextmanager
from backend.logging_setup import setup_logger

logger = setup_logger("db_helper")


@contextmanager
def get_db_cursor(commit=False):
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "root"),
            database=os.getenv("MYSQL_DATABASE", "expense_manager"),
        )

        cursor = connection.cursor(dictionary=True)
        yield cursor

        if commit:
            connection.commit()

    except Exception:
        if connection and connection.is_connected():
            connection.rollback()
        logger.exception("Database operation failed")
        raise

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def fetch_expenses_for_date(expense_date):
    logger.info(f"fetch_expenses_for_date called with {expense_date}")

    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM expenses WHERE expense_date = %s",
            (expense_date,),
        )
        return cursor.fetchall()


def delete_expenses_for_date(expense_date):
    logger.info(f"delete_expenses_for_date called with {expense_date}")

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "DELETE FROM expenses WHERE expense_date = %s",
            (expense_date,),
        )


def insert_expense(expense_date, amount, category, notes):
    logger.info(
        f"insert_expense called with date: {expense_date}, "
        f"amount: {amount}, category: {category}"
    )

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """INSERT INTO expenses
               (expense_date, amount, category, notes)
               VALUES (%s, %s, %s, %s)""",
            (expense_date, amount, category, notes),
        )


def fetch_expense_summary(start_date, end_date):
    logger.info(
        f"fetch_expense_summary called with start: {start_date}, "
        f"end: {end_date}"
    )

    with get_db_cursor() as cursor:
        cursor.execute(
            """SELECT category, SUM(amount) AS total
               FROM expenses
               WHERE expense_date BETWEEN %s AND %s
               GROUP BY category""",
            (start_date, end_date),
        )
        return cursor.fetchall()


if __name__ == "__main__":
    expenses = fetch_expenses_for_date("2024-09-30")
    print(expenses)

    summary = fetch_expense_summary("2024-08-01", "2024-08-05")
    for record in summary:
        print(record)
