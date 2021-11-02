from werkzeug.utils import redirect
from flask import Flask, flash, g, render_template, request
import pandas as pd

from stored.XLSXparser import parse_xlsx

# Flask app init
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = '511312c97a7bfbdaaee96cde'
@app.route("/")
def redirecthome():
    return redirect("/home")


@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/import")
def import_kw():
    return render_template('import.html')


@app.route("/import/xlsximport", methods=['POST', 'GET'])
def import_xlsx():
    if request.method == "POST":
        df1 = pd.read_excel(request.files['xlsxfile'], header=2)
        parse_xlsx(df1)
        # return redirect('/import/missing-value')
        return redirect('/home')


app.run(debug=True)
