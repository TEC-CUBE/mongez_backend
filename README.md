# oncology-backend

microservices and API services

## Requirements
- python == 3.8
- pip

## Deploy to sas server
ssh root@10.255.0.4

## Development
```bash
$ python -m venv venv
$ pip install -r requirements
$ flask db init
$ flask db migrate
$ flask db upgrade
$ export FLASK_APP=app
$ export DATABASE_URL='db_connection_string'
$ flask run
```
## Deployment
```bash
$ zappa update dev || zappa deploy dev

```

## Debugging
##### Local environment:
```
$ export FLASK_DEBUG=1
```
##### AWS environment:
```bash
$ zappa tail dev 
```

## Digarams


##### Database ERD diagram
- Load database.xml file using [the erd tool](https://ondras.zarovi.cz/sql/demo/)

## Contributing
- [Conventional commit messages](https://github.com/conventional-changelog/conventional-changelog/blob/a5505865ff3dd710cf757f50530e73ef0ca641da/conventions/angular.md)
- [Issues / Featurs](https://github.com/CodeToRelax/venice-store-backend/issues)
