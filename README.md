# Flask Project: Interactive Login and Database Interaction

This Flask project demonstrates how to create an interactive HTML interface where users are prompted to log in with their ID to access and pull information from a database. It leverages Flask, HTML, and SQL to provide a seamless user experience.

## Table of Contents

1. [Introduction](#introduction)
2. [Setup](#setup)
3. [Usage](#usage)
4. [Contributing](#contributing)
5. [License](#license)

## Introduction

In many web applications, user authentication is a crucial aspect. This project focuses on implementing a simple yet effective login system using Flask, where users are required to input their ID to access specific information stored in a database.

## Setup

To run this Flask project on your local machine, follow these steps:

1. Clone the repository:

```
git clone https://github.com/your_username/flask-project.git
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure you have a database set up and accessible. Update the `config.py` file with your database credentials.

## Usage

After completing the setup, you can run the Flask application:

```bash
python app.py
```

This will start the Flask development server, and you can access the application by navigating to `http://localhost:5000` in your web browser.

The application will present an HTML form where users can input their ID to log in. Upon successful login, the application will fetch information from the database corresponding to the user's ID and display it on the web page.

## Contributing

Contributions to improve the functionality and user experience of this Flask project are welcome! If you have suggestions for enhancements or encounter any issues, please feel free to open an issue or create a pull request.

## License

This project is licensed under the [MIT License](LICENSE). You are free to use and modify the code as needed.
