# Readme

This projects source code follows a standard Django webapp structure. The top folder contains the files to run the system - manage.py
The Classifier-_website folder contains the Django setting and urls
The personal_classifier contains all of the processing/ templates that are needed for Django to run the application.
Templates contains all of the HTML templates
python_files contains the classifier
static contains the CSS and javascript files

## Build instructions

The system does not need to the email collection to run, it should already have stored the necessary data in the database. This means the classifier does not need to be run for the system to work.

Navigate to the folder containing environment.yml and run
conda env create -f environment.yml

navigate to the folder containing manage.py and run
python manage.py runserver


### Requirements

* Python 3.7
* conda 22.9.0
* Tested on Windows 10 and 11

### Build steps

* navigate to folder containing environment.yml
* `conda env create -f environment.yml`
* navigate to folder containing manage.py 
* `python manage.py runserver`

* If you would like to run the classifier you need to download the collection from https://gitlab.com/Lemish891/identifying-and-protecting-personal-information-in-email-search/-/tree/main/data/ and download the enron_with_categories folder

* You will have to wipe the databse by navigating to the folder containing manage.py and running
* `python manage.py flush`
* and then proced to rebuild the database by running 
* `python manage.py migrate`
* `python manage.py makemigrations`
* you can then run the server
* `python manage.py runserver`
* and use the submit and upload buttons to run the classifier
* WARNING the classifier takes between 10-15 minutes to run 

### Test steps

* WARNING the tests run the classifier over the whole collection therefore by running the test the classifier will take between 10 - 15 minutes to run.
* Run automated tests by navigating to folder containing manage.py and running `python manage.py test`

* Start the software by running `python manage.py runserver`

