import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import math
import struct

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()
    end = datetime.datetime.now(pytz.timezone("US/Eastern"))
    start = end - datetime.timedelta(days=7)

    # Yahoo Finance API
    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
        f"?period1={int(start.timestamp())}"
        f"&period2={int(end.timestamp())}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )

    # Query API
    try:
        response = requests.get(
            url,
            cookies={"session": str(uuid.uuid4())},
            headers={"User-Agent": "python-requests", "Accept": "*/*"},
        )
        response.raise_for_status()

        # CSV header: Date,Open,High,Low,Close,Adj Close,Volume
        quotes = list(csv.DictReader(response.content.decode("utf-8").splitlines()))
        quotes.reverse()
        price = round(float(quotes[0]["Adj Close"]), 2)
        return {"name": symbol, "price": price, "symbol": symbol}
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def binary_to_integer(binary_str):
    # Reverse the binary string to process digits from right to left
    binary_str = binary_str[::-1]

    decimal = 0
    for i in range(len(binary_str)):
        if binary_str[i] == "1":
            decimal += 2**i

    return decimal


def int_to_binary(number):
    if number == 0:
        return "0b0"

    binary_digits = []
    while number > 0:
        binary_digits.append(str(number % 2))
        number //= 2

    binary_digits.reverse()
    return "" + "".join(binary_digits)


def signed_subtraction(num1, num2):
    # Ensure both numbers are 16 bits
    num1 = num1.zfill(16)
    num2 = num2.zfill(16)

    # Ensure the numbers are in two's complement representation
    if num1[0] != num2[0]:
        # If the signs are different, perform addition instead of subtraction
        return signed_addition(num1, complement(num2))

    # If the signs are the same, perform regular subtraction
    result = ""
    borrow = 0

    for i in range(15, 0, -1):  # Start from the least significant bit
        bit1 = int(num1[i])
        bit2 = int(num2[i])
        subtracted_bit = bit1 - bit2 - borrow

        if subtracted_bit < 0:
            subtracted_bit += 2
            borrow = 1
        else:
            borrow = 0

        result = str(subtracted_bit) + result

    # Handle the sign bit
    result = num1[0] + result

    # Check for underflow (negative overflow)
    if result[0] != num1[0]:
        raise ArithmeticError("Signed subtraction resulted in underflow")

    return result


def signed_addition(num1, num2):
    # Ensure both numbers are 16 bits
    num1 = num1.zfill(16)
    num2 = num2.zfill(16)

    # Ensure the numbers are in two's complement representation
    if num1[0] != num2[0]:
        # If the signs are different, perform subtraction instead of addition
        return signed_subtraction(num1, complement(num2))

    # If the signs are the same, perform regular addition
    result = ""
    carry = 0

    for i in range(15, 0, -1):  # Start from the least significant bit
        bit1 = int(num1[i])
        bit2 = int(num2[i])
        added_bit = bit1 + bit2 + carry

        if added_bit >= 2:
            added_bit -= 2
            carry = 1
        else:
            carry = 0

        result = str(added_bit) + result

    # Handle the sign bit
    result = num1[0] + result

    # Check for overflow
    if result[0] != num1[0]:
        raise ArithmeticError("Signed addition resulted in overflow")

    return result


# Helper function to calculate the two's complement of a binary number
def complement(binary):
    complemented = ""
    for bit in binary:
        complemented += "1" if bit == "0" else "0"
    return complemented


# Now code a function to do 32 bit floating point biary addition


# funcion to convert float to IEEE binary num
def float_to_binary(float_number):
    if float_number == 0:
        return "0" * 32

    # Handle special cases: NaN, infinity, and denormalized numbers
    if abs(float_number) == float("inf") or math.isnan(float_number):
        return "0" * 32

    # Handle sign bit
    sign_bit = "1" if float_number < 0 else "0"

    # Convert the float to its binary representation
    float_bits = bin(struct.unpack("!I", struct.pack("!f", float_number))[0])[2:]

    # Normalize and format the binary representation
    exponent = float_bits.find("1")
    normalized_bits = float_bits[exponent + 1 :].ljust(23, "0")

    # Exponent bias for IEEE 32-bit format
    exponent_bias = 127

    # Calculate the exponent field
    exponent_field = format(exponent + exponent_bias, "08b")

    # Combine the sign bit, exponent field, and mantissa to get the IEEE 32-bit binary
    ieee_32bit_binary = sign_bit + exponent_field + normalized_bits

    return ieee_32bit_binary


def float_to_hex(float_number):
    try:
        # Handle special cases: NaN, infinity, and denormalized numbers
        if abs(float_number) == float("inf") or math.isnan(float_number):
            return "0x7fffffff" if float_number > 0 else "0xffffffff"

        # Convert the float to its binary representation
        float_bits = bin(struct.unpack("!I", struct.pack("!f", float_number))[0])[2:]

        # Normalize the binary representation
        exponent = float_bits.find("1")
        normalized_bits = float_bits[exponent + 1 :].ljust(23, "0")

        # Exponent bias for IEEE 32-bit format
        exponent_bias = 127

        # Calculate the exponent field
        exponent_field = format(exponent + exponent_bias, "08b")

        # Combine the sign bit, exponent field, and normalized bits
        ieee_32bit_binary = exponent_field + normalized_bits

        # Convert the binary representation to hexadecimal
        hex_result = hex(int(ieee_32bit_binary, 2))[2:]
        return hex_result
    except Exception as e:
        return str(e)






def binary_to_float(binary_pattern):
    try:
        # Pad the binary pattern with zeros to make it 32 bits long
        binary_pattern = binary_pattern.zfill(32)

        # Check for special cases
        if binary_pattern == "00000000000000000000000000000000":
            return 0.0
        elif binary_pattern == "01111111100000000000000000000000":
            return float('inf')
        elif binary_pattern == "11111111100000000000000000000000":
            return float('-inf')
        elif binary_pattern == "01111111110000000000000000000000":
            return float('nan')

        # Convert the binary pattern to an integer
        integer_value = int(binary_pattern, 2)

        # Unpack the integer as a 32-bit floating-point number
        float_result = struct.unpack("!f", struct.pack("!I", integer_value))[0]

        return float_result
    except Exception as e:
        return str(e)



def twos_complement(binary_str):
    # Step 1: Invert all bits
    inverted_str = "".join(["1" if bit == "0" else "0" for bit in binary_str])

    # Step 2: Add 1 to the inverted binary number
    carry = 1
    result = ""
    for bit in reversed(inverted_str):
        if bit == "0" and carry == 1:
            result = "1" + result
            carry = 0
        elif bit == "1" and carry == 1:
            result = "0" + result
        else:
            result = bit + result

    return result


def float_add(a_bin, b_bin):
    # Extract the sign bit, exponent bits, and mantissa bits of both numbers
    sign_a = int(a_bin[0])
    sign_b = int(b_bin[0])

    exponent_a = int(a_bin[1:9], 2)
    exponent_b = int(b_bin[1:9], 2)

    mantissa_a = '1' + a_bin[9:]
    mantissa_b = '1' + b_bin[9:]

    # Calculate the new exponent after aligning the binary points
    max_exponent = max(exponent_a, exponent_b)
    diff_exponent_a = max_exponent - exponent_a
    diff_exponent_b = max_exponent - exponent_b

    if diff_exponent_a > 0:
        mantissa_a = '1' + mantissa_a + '0' * diff_exponent_a
    else:
        mantissa_b = '1' + mantissa_b + '0' * diff_exponent_b

    # Perform binary addition on mantissas
    result_mantissa = bin(int(mantissa_a, 2) + int(mantissa_b, 2))[2:]

    # Handle overflow in mantissa
    if len(result_mantissa) > 24:
        result_mantissa = result_mantissa[1:]
        max_exponent += 1

    # Normalize the result mantissa
    while len(result_mantissa) < 24:
        result_mantissa += '0'

    # Create the result binary string
    result_sign = '0' if sign_a == sign_b else '1'
    result_exponent = format(max_exponent, '08b')
    result_binary = result_sign + result_exponent + result_mantissa

    result_binary = result_binary.replace('-', '')

    return result_binary


def float_sub(a_bin, b_bin):

    # Extract the sign bit, exponent bits, and mantissa bits of both numbers
    sign_a = a_bin[0]
    sign_b = b_bin[0]

    exponent_a = a_bin[1:9]
    exponent_b = b_bin[1:9]

    mantissa_a = a_bin[9:]
    mantissa_b = b_bin[9:]

    # Check if the numbers are the same (excluding the sign)
    if exponent_a == exponent_b and mantissa_a == mantissa_b:
        return '0' * 32  # Return all zeros if they are the same

    # Calculate the new exponent after aligning the binary points
    max_exponent = max(int(exponent_a, 2), int(exponent_b, 2))
    diff_exponent_a = max_exponent - int(exponent_a, 2)
    diff_exponent_b = max_exponent - int(exponent_b, 2)

    if diff_exponent_a > 0:
        mantissa_a = '1' + mantissa_a + '0' * diff_exponent_a
    else:
        mantissa_b = '1' + mantissa_b + '0' * diff_exponent_b

    # Perform binary subtraction on mantissas
    result_mantissa = bin(int(mantissa_a, 2) - int(mantissa_b, 2))[2:]

    # Handle underflow in mantissa
    while result_mantissa[0] != '1':
        result_mantissa = result_mantissa[1:]
        max_exponent -= 1

    # Normalize the result mantissa
    while len(result_mantissa) < 24:
        result_mantissa = '0' + result_mantissa

    # Create the result binary string
    result_sign = '0' if sign_a == sign_b else '1'
    result_exponent = format(max_exponent, '08b')
    result_binary = result_sign + result_exponent + result_mantissa

    result_binary = result_binary.replace('-', '')

    return result_binary



def float_mul(a_bin, b_bin):
    # Extract the sign bit, exponent bits, and mantissa bits of both numbers
    sign_a = int(a_bin[0])
    sign_b = int(b_bin[0])

    exponent_a = int(a_bin[1:9], 2)
    exponent_b = int(b_bin[1:9], 2)

    mantissa_a = '1' + a_bin[9:]
    mantissa_b = '1' + b_bin[9:]

    # Calculate the new exponent and multiply mantissas
    result_exponent = exponent_a + exponent_b - 127
    result_mantissa = bin(int(mantissa_a, 2) * int(mantissa_b, 2))[2:]

    # Normalize the result mantissa
    while len(result_mantissa) > 24:
        result_mantissa = result_mantissa[1:]
        result_exponent += 1

    while len(result_mantissa) < 24:
        result_mantissa = '0' + result_mantissa

    # Create the result binary string
    result_sign = '0' if sign_a == sign_b else '1'
    result_exponent = format(result_exponent, '08b')
    result_binary = result_sign + result_exponent + result_mantissa

    result_binary = result_binary.replace('-', '')

    return result_binary



'''
# Example usage with 32-bit binary strings:
a_binary = "01000000010000000000000000000000"  # Represents 2.0 in IEEE 754 format
b_binary = "11000000011000000000000000000000"  # Represents -3.0 in IEEE 754 format

result = binary_float_subtraction(a_binary, b_binary)
print(f"The result is: {result}")
'''