# FlaskApp - TOVE

Simple application with authentication and CRUD functionality using the Python Flask micro-framework

The Installation instruction is referenced for web-server running on Linux.

## Installation

To use this template, your computer needs:

- [Python 2 or 3](https://python.org)
- [Pip Package Manager](https://pypi.python.org/pypi)


## Install Python Package
```
pip2 install flask

pip2 install flask-mysqldb

pip2 install Flask-WTF

pip2 install passlib
```


## Install Mysql

```
# I set password to '1122'
sudo apt-get install mysql-server libmysqlclient-dev
```


## (Installation Part) Create Mysql Database

```
mysql -u root -p

create database myflaskapp;

use myflaskapp;

create table users(username varchar(100) PRIMARY KEY, department varchar(30), password varchar(100));

create table activities(username varchar(100), activity varchar(200));

create table inform_admin(id int AUTO_INCREMENT PRIMARY KEY, operation varchar(20), activity varchar(200));

create table inform_user(id int AUTO_INCREMENT PRIMARY KEY, username varchar(100), activity varchar(200));
```


### Running the app

```bash
python2 app.py
```

### Running the Mysql

```
mysql -u root -p
```