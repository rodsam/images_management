#Your Gallery

This website is build for exhibit great photo shoot by people. and visitor could comment on these photos.

It's base on python3.6 and sqlite.

### Application architecture

├── app
│   ├── admin         // Admin routes for admin control
│   ├── auth          // Auth routes for user login and register
│   ├── main          // Main routes for front-side
│   ├── static        // Static file like js, css, and img 
│   ├── templates     // Templates file for jinja2
│   ├── __init__.py   // init file for module app
│   ├── models.py     // modle file of user, imgae, comment
│   └── utils.py      // tool function file
├── app.db            // Database file
├── app.py            // Entrance of the project
├── auth.json         // Google Auth file
├── config.py         // Configure of project
├── migrations        // Datebase migration file
├── README.md         // README file
└── requirements.txt  // Requiements libs for project


### Dependencies

[Flask](http://flask.pocoo.org/)

[SQLAlchemy](https://www.sqlalchemy.org/)

[Flask-WTF](https://flask-wtf.readthedocs.io/)

[Flask-Login](https://flask-login.readthedocs.io/en/latest/)

[Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/)

[Jquery](https://jquery.com/)

[BootStrap](https://getbootstrap.com/)

[google-cloud-storage](https://pypi.org/project/google-cloud-storage/)

### Reference

All the image used in this site comes from  [Unsplash](https://unsplash.com/@fotografierende)


### Deploy 

- Set up you Google cloud accout and your bucket, generate your auth.json then copy it to project directory.

- Change the `GOOGLE_AUTH` to you auth.json file's name  and `BUCKET_NAME` to your bucket's name.

- Open the directory and run `pip install -r requirements.txt` in the command line to get all the libs needed for the project.

- Then `export FLASKAPP=app.py` to claim the entrance of the project

- `flask run` to get the server run, and you could use `flask run -h YOUR_HOST_IP_or_0.0.0.0 -p YOUR_PORT` to run up wioth a custom config.

- Open you broswer and input `localhost:5000` or `YOUR_HOST_IP:YOUR_PORT` to explore this site.


