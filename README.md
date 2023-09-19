# Library Management System (LMS)

The Library Management System (LMS) is a simple web application built using Flask and MySQL that allows you to manage books, library members, and book transactions. This README provides an overview of the project, installation instructions, available endpoints, and usage examples.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Available Endpoints](#available-endpoints)
4. [Database Setup](#database-setup)
5. [Usage](#usage)
## Introduction

The Library Management System (LMS) is designed to help library administrators and staff manage their book inventory and member records efficiently. It offers a set of APIs for tasks such as adding, updating, deleting, and searching for books and members, as well as issuing and returning books with late fee calculation.

## Installation

Before running the LMS, ensure you have Python and MySQL installed. Follow these steps to set up and run the application:

1. Clone the repository:

   ```bash
   git clone https://github.com/Ansh060901/Library_Management.git

2. Create a virtual environment in that folder using following command:

   ```bash
   python -m venv venv
   venv\Scripts\activate

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   
## Endpoint Documentation

1. GET /get_book/int:book_id

   This endpoint allows you to retrieve details of a book by its ID.
   
   Status Codes:

   200 OK: The book details were successfully retrieved.
   404 Not Found: The book with the specified ID was not found.


2. POST /add_book
   
   This endpoint allows you to add a new book to the library.

## Database Setup

   The LMS uses MySQL as its database. Before running the application, create a MySQL database named interview and configure the database connection in the main.py file as needed.
   

## Usage

   To start the LMS, run the following command:

   ```bash
   python app.py
