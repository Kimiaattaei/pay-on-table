# pay on table

pay on table is a python project for shop and pay with scan QR code :iphone: :money_with_wings:

## Installation
you need python3 and pip for install requirements after get project with git clone

```python
pip install -r requirements.txt
```

next step

```python
python manage.py makemigrations && python manage.py migrate
```

now you should create superuser for admin

```python
python manage.py createsuperuser
```

now you can run server and use this website
```python
python manage.py runserver
```

you can go to swagger/ for see what dose this site have
and go to admin/ and sign in with your superuser that you create and manage your website