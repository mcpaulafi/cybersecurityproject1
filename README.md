# KumpulaSalon Booking

This project is created for course Cyber Security Base: Course Project I (TKT200093) in University of Helsinki in August 2025.
The app demostrates following 5 security flaws and their fixes:
1. Cross-site Request Forgery
2. Broken Access Control
3. Injection
4. Identification and Authentication Failures
5. Security Misconfiguration

### Flaws

- View [screenshots of flaws](https://github.com/mcpaulafi/cybersecurityproject1/tree/main/screenshots)
- [PDF report](https://github.com/mcpaulafi/cybersecurityproject1/blob/main/screenshots/flaw_documentation.pdf)

## Features

- Django web application
- Custom extension to password recovery functionality
- Uses Poetry for dependency management
- Coverage reporting for tests

## Prerequisites

- Python 3.11+
- Poetry installed (pip install poetry)

## Setup

1. Clone the repository
```bash
git clone https://github.com/mcpaulafi/cybersecurityproject1.git
```

2. Install dependencies with Poetry
```bash
poetry install
```

3. Activate virtual environment
```bash
poertry shell
```

4. Apply migrations
```bash
python3 manage.py migrate
```

5. Create a superuser
```bash
python3 manage.py createsuperuser
```

## Running the app

1. Run the development server
```bash
python3 manage.py runserver
Open http://127.0.0.1:8000 in your browser
```

2. Login to admin pages
```bash
http://127.0.0.1:8000/admin
```

3. On admin pages add future (bookable) appointment times and create users

4. Login to book appointments etc.
```bash
http://127.0.0.1:8000/
```


## Running tests

1. Running tests
```bash
python3 manage.py test
```

2. Running coverage
```bash
coverage run --source=pages manage.py test
coverage report -m
coverage html  # Generates HTML report in htmlcov/
```

3. Running pylint
```bash
pylint .
```

## Known issues

With Google Chome browser (Version 139.0.7258.154) on Ubuntu, HTML dropdown list shows up on the left top corner of the browser and not at the position it is on the page layout. It works on Firefox though.
