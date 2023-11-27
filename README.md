<h2 align="center">🕵🏼‍♂️ Scrapping upwork.com</h2>
<h4 align="center">Login into the site upwork.com and catch some information.</h4>
<h2 align="center">
<img alt="GitHub followers" src="https://img.shields.io/github/followers/Alfareiza?label=Follow%20me%20%3A%29&style=social">
</h2>

<h1 align="center" >
    <img src="resources/output_cli.gif">
</h1>

This scrapper/scanner logs into a Upwork account using selenium for the login process, catches all the jobs which are in the main page through a local file created with python and consumed with BeautifoulSoup. Then it navigates to the profile page with selenium, extracts certain information about the profile owner using BeautifoulSoup. Finally, I used pydantic to model the  scrapped data and export it into a JSON file.

I also used mypy, flake8 and pytest for checks, linting and testing, besides of typer to facilitate easy and expandable interaction with the CLI.

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
