<h2 align="center">🕵🏼‍♂️ Scrapping upwork.com</h2>
<h4 align="center">Login into the site upwork.com and catch some information.</h4>
<h2 align="center">
<img alt="GitHub followers" src="https://img.shields.io/github/followers/Alfareiza?label=Follow%20me%20%3A%29&style=social">
</h2>

This scrapper get in to a upwork account, catch all the jobs which are in the main page, then go to the profile page and
catch also the information of the account.

## Table of Contents

- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
- [Linting and Checks](#linting-and-checks)
- [Tests](#tests)

## Getting Started

The next command will execute the process of scanner in the site upwork.com

```bash
python scan.py upwork
```

### Prerequisites

#### 1. Clone the Project

Execute the next command on your terminal

```bash
git clone https://github.com/Alfareiza/scrap-up-work-com.git
```

#### 2. Isolate the environment

Once the repository has been cloned, a folder is created with the name of the project `scrap-up-work-com`.

Go toward this folder using the terminal :

```bash
cd scrap-up-work-com
```

Make sure you have python 3.11 installed and execute:

```bash
python -m venv .venv
```

Then to activate the isolated environment execute the next command according to your O.S

| Windows                |           Linux           |
|------------------------|:-------------------------:|
| .venv\Scripts\activate | source .venv/bin/activate |

### Installation

All the dependencies and sub-dependencies will be installed on the local project.

```bash
pip install poetry
```

```bash
poetry install
```

## Linting and Checks

Type checker.

```bash
mypy .
```

Linting tool for checking pep8 recommendations.

```bash
flake8 --exclude .venv --ignore=E501,F401
```

## Tests

Execution of tests.

```bash
pytest  .
```
