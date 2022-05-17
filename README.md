# Invo Financial Spreadsheet

Invo Finance Spreadsheet is an opensource personal finance spreadsheet developed on Django that helps individual users keep track of their financial income and expenses on a monthly basis.

We welcome code contributions, suggestions, and feature requests via github.

## Setup

##### Setup env using the following command in the project folder

```bash
python3 -m venv invo-venv
```

##### Activate env with the following command in the project folder

```bash
source invo-venv/bin/activate
```

##### Install requirements

```bash
pip install -r requirements.txt
```

Create a .env file to keep all env variables with their respective values. The variables names are located in .env-example

##### Migrate Database

```bash
python manage.py makemigrations
python manage.py migrate
```

##### Load data to preload Database
Load data to country and state tables using json files in "board/fixtures" folder. please check below command for reference.

```bash
python manage.py loaddata country_data.json
python manage.py loaddata state_data.json
```
