from passwords import PasswordSettings, PasswordGenerator
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    settings = PasswordSettings() if request.method != 'POST' else \
        PasswordSettings(length=int(request.form.get('length')),
                         use_lowercase=request.form.get('use_lowercase'),
                         use_uppercase=request.form.get('use_uppercase'),
                         use_numbers=request.form.get('use_numbers'),
                         use_special=request.form.get('use_special'),
                         min_numbers=int(request.form.get('min_numbers')),
                         min_special=int(request.form.get('min_special')))

    if not settings.is_valid():
        return render_template('index.html', settings=settings)

    password = PasswordGenerator().generate(settings)
    return render_template('index.html', password=password, settings=settings)


@app.route('/about')
def about(name=None):
    return render_template('about.html', name=name)
