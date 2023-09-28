import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import re  # Importing regular expression module for pattern matching
import datetime


from helpers import (
    apology,
    login_required,
    lookup,
    binary_to_integer,
    usd,
    int_to_binary,
    signed_addition,
    signed_subtraction,
    float_to_hex,
    float_to_binary,
    binary_to_float,
    twos_complement,
    float_add,
    float_mul,
    float_sub,
)

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///binary.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
# @login_required
def index():
    if request.method == "GET":
        return render_template("index.html")

    num1 = str(request.form.get("num1"))
    num2 = str(request.form.get("num2"))

    for digit1, digit2 in zip(num1, num2):
        if digit1 not in ["0", "1"] or digit2 not in ["0", "1"]:
            return apology("Not a binary number", 400)

    operation = request.form.get("operation")
    if not operation:
        return apology("Must specify the operation", 400)

    result = None  # Initialize result variable

    if operation == "add":  # Addition
        result = bin(int(num1, 2) + int(num2, 2))[2:]
        decimal = int(result, 2)
    elif operation == "sub":  # Subtraction
        result = bin(int(num1, 2) - int(num2, 2))[2:]
        decimal = int(result, 2)
    elif operation == "mul":  # Multiplication
        result = bin(int(num1, 2) * int(num2, 2))[2:]
        decimal = int(result, 2)
    elif operation == "div":  # Division
        try:
            dividend = int(num1, 2)
            divisor = int(num2, 2)

            # Perform division
            quotient = dividend // divisor
            remainder = dividend % divisor

            # Convert quotient and remainder back to binary
            quotient = bin(quotient)[2:]
            remainder = bin(remainder)[2:]
            result = (quotient, remainder)

        except ZeroDivisionError:
            return apology("Division by zero is not allowed", 400)
    else:
        return apology("Invalid operation", 400)

    if "user_id" in session:
        user_id = session["user_id"]
        time = datetime.datetime.now()
        # insert into table operations
        if operation in ["div"]:
            db.execute(
                "INSERT INTO operations (user_id, num1, op, num2, result, time) VALUES (?, ?, ?, ?, ?, ?)",
                user_id,
                num1,
                operation,
                num2,
                result[0],
                time,
            )
            decimal = int(result[0], 2)

        db.execute(
            "INSERT INTO operations (user_id, num1, op, num2, result, time) VALUES (?, ?, ?, ?, ?, ?)",
            user_id,
            num1,
            operation,
            num2,
            result,
            time,
        )

        # Pass the result to the template to display it to the user
        return render_template(
            "result.html",
            result=result,
            first=num1,
            operation=operation,
            second=num2,
            decimal=decimal,
        )

    else:
        # Pass the result to the template to display it to the user
        return render_template(
            "result.html", result=result, first=num1, operation=operation, second=num2
        )


@app.route("/reset", methods=["POST"])
def reset():
    return redirect(url_for("index"))


@app.route("/tips_tricks")
@login_required
def tips_and_tricks():
    return render_template("tips_and_tricks.html")


@app.route("/documentation")
def documentation():
    return render_template("documentation.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    op_db = db.execute(
        "SELECT * FROM operations WHERE user_id = :id ORDER BY TIME DESC", id=user_id
    )
    return render_template("history.html", operations=op_db)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        name = db.execute("SELECT name FROM users WHERE id = ?", (session["user_id"]))
        if name:
            flash(f"Welcome Back, {name[0]['name'].capitalize()}")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/convert", methods=["GET", "POST"])
@login_required
def convert():
    if request.method == "GET":
        return render_template("convert.html")
    else:
        number = request.form.get("input").strip()
        op = request.form.get("conversionType")

        if not number:
            return apology("Must provide a number")

        result = None  # Initialize result with None
        hex_result = None

        if op == "binary_to_decimal":
            for i in range(len(number)):
                if number[i] not in ["0", "1"]:
                    return apology("Not a binary number")
            result = int(number, 2)
            hex_result = hex(result)[2:]
        elif op == "decimal_to_binary":
            for digit in number:
                if not digit.isdigit():
                    return apology("Not a valid number")
            decimal_number = int(number)
            result = bin(decimal_number)[2:]
            hex_result = hex(decimal_number)[2:]
        elif op == "float_to_binary":
            try:
                float_number = float(number)
                hex_result = float_to_hex(float_number)
            except ValueError:
                return apology("Not a valid floating-point number")

            result = float_to_binary(float_number)
        elif op == "binary_to_float":
            if re.match(r"^[01]{32}$", number):
                result = binary_to_float(number)
                hex_result = float_to_hex(result)
                print(number, op, result, hex_result)  # Debugging statement
            else:
                return apology("Not a valid 32-bit binary number")

        elif op == "twos_complement":
            for i in range(len(number)):
                if number[i] not in ["0", "1"]:
                    return apology("Not a binary number")
            result = twos_complement(number)
            hex_result = hex(int(number, 2))[2:]
        # if result is None:
        #   return apology("Invalid operation or input")
        if "user_id" in session:
            user_id = session["user_id"]
            time = datetime.datetime.now()
            # insert into table operations
            db.execute(
                "INSERT INTO operations (user_id, num1, op, num2, result, time) VALUES (?, ?, ?, ?, ?, ?)",
                user_id,
                number,
                op,
                result,
                result,
                time,
            )

        return render_template(
            "result.html", num=number, operation=op, result=result, hex=hex_result
        )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # Checking username and password

    name = request.form.get("name").strip()
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    confirmation = request.form.get("confirmation").strip()

    # Check if username is blank or already exists
    if (
        not username
        or len(db.execute("SELECT username FROM users WHERE username = ?", (username,)))
        > 0
    ):
        return apology("Invalid username: Blank, or already exists")

    # Check if password is blank or doesn't match confirmation
    if not password or password != confirmation:
        return apology("Invalid password: Blank, or passwords don't match")

    # Check if password has at least 6 characters
    if len(password) < 6:
        return apology("Invalid password: Password must be at least 6 characters long")

    # Check if username starts with an alphabet character (case-insensitive)
    if not re.match(r"^[A-Za-z]", username):
        return apology(
            "Invalid username: Username must start with an alphabet character"
        )

    # Insert the new user into the database
    db.execute(
        "INSERT INTO users (username, hash, name) VALUES (?, ?, ?)",
        username,
        generate_password_hash(password),
        name,
    )

    # Retrieve the newly registered user's information
    rows = db.execute("SELECT * FROM users WHERE username = ?", username)

    # Set the user_id in the session for authentication purposes
    session["user_id"] = rows[0]["id"]
    flash(f"Welcome {name}")

    # Redirect the user to the home page
    return redirect("/")


@app.route("/arithmetic", methods=["GET", "POST"])
@login_required
def arithmetic():
    if request.method == "GET":
        return render_template("arithmetic.html")
    elif request.method == "POST":
        num1 = request.form.get("num1").strip()
        num2 = request.form.get("num2").strip()
        operation = request.form.get("op")

        if (
            not all(char in "01" for char in num1)
            or not all(char in "01" for char in num2)
            or len(num1) != len(num2)
        ):
            return apology("Input must be binary numbers of same lenght")

        result = None

        if operation == "Signed_add":
            try:
                result = signed_addition(num1, num2)
                decimal = int(result, 2)
            except ArithmeticError:
                return apology("Result is out of range for the given number of bits")
        elif operation == "Signed_sub":
            try:
                result = signed_subtraction(num1, num2)
                decimal = int(result, 2)
            except ArithmeticError:
                return apology("Result is out of range for the given number of bits")
        elif operation == "float_add":
            if len(num1) != 32 or len(num2) != 32:
                return apology("Input must be 32 bit binary number(s)")
            result = float_add(num1, num2)
            decimal = binary_to_float(result)
            print(decimal)
        elif operation == "float_sub":
            if len(num1) != 32 or len(num2) != 32:
                return apology("Input must be 32 bit binary number(s)")
            result = float_sub(num1, num2)
            decimal = binary_to_float(result)
        elif operation == "float_mul":
            if len(num1) != 32 or len(num2) != 32:
                return apology("Input must be 32 bit binary number(s)")
            result = float_mul(num1, num2)
            decimal = binary_to_float(result)
        elif operation == "Left_shift":
            result = num1 + num2
            decimal = int(result, 2)
        elif operation == "Right_shift":
            result = num1[: -len(num2)]
            decimal = int(result, 2)

        elif operation == "AND":
            result = "".join(
                ["1" if a == "1" and b == "1" else "0" for a, b in zip(num1, num2)]
            )
            decimal = int(result, 2)

        elif operation == "OR":
            # Bitwise OR operation on binary numbers
            # Assumes num1 and num2 are binary strings of the same length
            result = "".join(
                ["1" if a == "1" or b == "1" else "0" for a, b in zip(num1, num2)]
            )
            decimal = 0

        elif operation == "XOR":
            # Bitwise XOR operation on binary numbers
            # Assumes num1 and num2 are binary strings of the same length
            result = "".join(["1" if a != b else "0" for a, b in zip(num1, num2)])
            decimal = 0
        if "user_id" in session:
            user_id = session["user_id"]
            time = datetime.datetime.now()
            # insert into table operations
            db.execute(
                "INSERT INTO operations (user_id, num1, op, num2, result, time) VALUES (?, ?, ?, ?, ?, ?)",
                user_id,
                num1,
                operation,
                num2,
                result,
                time,
            )

            # Pass the result to the template to display it to the user
        return render_template(
            "result.html",
            result=result,
            first=num1,
            operation=operation,
            second=num2,
            decimal=decimal,
        )
