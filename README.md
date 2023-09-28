# Binary Calculator Web Application
Video Demo:  https://youtu.be/8A072BUgyvI?si=pwWlRCk3FWI-m-Mj
This is a simple web application as part of my CS50x final project for performing binary arithmetic operations and conversions. You can use this application to perform various binary operations, such as addition, subtraction, multiplication, and division, as well as convert between binary and decimal representations.

## Features

1. **Binary Arithmetic:** You can perform binary addition, subtraction, multiplication, and division. The application ensures that the inputs are valid binary numbers before performing the operation.

2. **Binary Conversions:**
   - Convert binary to decimal: Convert a binary number to its decimal representation.
   - Convert decimal to binary: Convert a decimal number to its binary representation.
   - Convert floating-point numbers to binary: Convert a floating-point number (e.g., 3.14159) to its IEEE 754 binary representation and vice versa.

3. **Twos Complement:** Calculate the two's complement of a binary number.

4. **Bitwise Operations:** Perform bitwise AND, OR, and XOR operations on two binary numbers.

5. **User Registration and History:** Users can register, log in, and track their binary operations and conversions history.

## Usage

1. **Homepage:** The homepage allows you to select the operation you want to perform, enter the binary numbers, and view the result. The available operations include addition, subtraction, multiplication, and division.

2. **Conversion:** You can access the binary number conversion tools by clicking on the "Convert" link in the navigation menu. Here, you can convert binary to decimal, decimal to binary, floating-point to binary, and binary to floating-point.

3. **Arithmetic:** Click on the "Arithmetic" link in the navigation menu to access the binary arithmetic tools. You can perform signed addition and subtraction on binary numbers, as well as floating-point addition, subtraction, and multiplication.

4. **Bitwise Operations:** The "Bitwise Operations" section allows you to perform bitwise AND, OR, and XOR operations on two binary numbers.

5. **History:** If you are registered and logged in, you can access your operations and conversions history by clicking on the "History" link in the navigation menu.

## Getting Started

To run the binary calculator web application locally, follow these steps:

1. Clone the repository to your local machine:

   ```
   git clone <repository-url>
   ```

2. Navigate to the project directory:

   ```
   cd binary-calculator
   ```

3. Install the required Python packages using pip:

   ```
   pip install -r requirements.txt
   ```

4. Set up the database by running the following commands:

   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Start the Flask development server:

   ```
   flask run
   ```

6. Open a web browser and go to `http://localhost:5000` to access the application.

## Technologies Used

- Python (Flask)
- SQLite database
- HTML/CSS
- JavaScript

## Acknowledgments

This web application was created as part of a project and may have limitations. If you encounter any issues or have suggestions for improvements, please feel free to contribute to the project or report them.

Enjoy using the Binary Calculator!
