# Project Reports Management 

A web application using Django REST Framework is a service of managing holding projects reports.

The Track and PMRS provides API for getting information about project progress along with providing dashboard reports for boards. 

This app has the following features:

- users can create/read/update/delete Base Info via rest api
- users can create/read/update/delete monthly report such as Invoices, Budgets, Machinery, Project Progress, ect via rest api
- users can create/read/update/delete projects documents and images shipments via rest api
- users can retrieve report from users activity in this system environment via rest api
- users can retrieve image reports from all zones of projects via rest api
- users can retrieve report from all projects reports every month via rest api


The application has been covered with unit tests.

____
## Requirements

- Python 3.8+
- Django 3.1

## Packages

- django
- django-rest-framework
- django-cors-headers 
- python-decouple
- drf-spectacular (Open API)

## Installing

1\. Clone the repository:
```
git clone https://github.com/AliSajadian/track_and_trace_api.git
```
2\. install requirements:
```
pip install -r requirements.txt
```
3\. create Postgresql database and user:
```

```
4\. migrate to database
```
python manage.py makemigrations
python manage.py migrate
```

## Usage




