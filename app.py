from flask import Flask, render_template, url_for, request, redirect, session, g
from logging import FileHandler, WARNING
from modelCreation import create_model
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from figures import fig1, fig2, fig3, fig4
import os
import datetime
import re


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


users = [User(id=1, username='admin', password='admin'), User(2, 'test', 'test'), User(3, 'user', 'user')]

zipcode_list = [98001, 98002, 98003, 98004, 98005, 98006, 98007, 98008, 98010,
                98011, 98014, 98019, 98022, 98023, 98024, 98027, 98028, 98029,
                98030, 98031, 98032, 98033, 98034, 98038, 98039, 98040, 98042,
                98045, 98052, 98053, 98055, 98056, 98058, 98059, 98065, 98070,
                98072, 98074, 98075, 98077, 98092, 98102, 98103, 98105, 98106,
                98107, 98108, 98109, 98112, 98115, 98116, 98117, 98118, 98119,
                98122, 98125, 98126, 98133, 98136, 98144, 98146, 98148, 98155,
                98166, 98168, 98177, 98178, 98188, 98198, 98199]

app_flask = Flask(__name__)
app_flask.secret_key = 'thisisasecretkey'

file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)

app_flask.logger.addHandler(file_handler)

app_dash = dash.Dash(__name__, server=app_flask,
                     routes_pathname_prefix='/visual/',
                     external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css'])

app_dash.layout = html.Div([
    html.Div(children=[
        html.Nav(className="navbar navbar-expand-lg navbar-light bg-light", children=[
            html.Img(
                src="/static/KCRlogo.jpg",
                style={
                    'height': '50px',
                    'width': '72px',
                    'margin-right': 10
                }),
            html.A(' Home Price Estimator', className="navbar-brand"),
            html.A('Estimation', className="nav-item nav-link btn", href='/main'),
            html.A('Data Visualization', className="nav-item nav-link active", style={'color': 'rgb(185,185,178)'}),
            html.Form(className="form-inline ml-md-auto", children=[
                html.A('Go Back', className="btn btn-sm btn-outline-secondary", href='/main', role='button')
            ])
        ])], className='container'),

    html.Div([
        html.Div([
            html.H2(children='Data Visualization:'),
            html.P(children='This dataset covers 21,613 home sales in King County, Washington between May 2014 and May 2015.'),
            html.Br()
        ], style={'background-color': 'white', 'margin-bottom': '-20px', 'padding-left': '20px'}),

        dcc.Graph(figure=fig1),
        dcc.Graph(figure=fig2),
        dcc.Graph(figure=fig3),
        dcc.Graph(figure=fig4)
    ], className='container', style={'margin-top': '20px'})
], style={'background-image': 'url("assets/seattleSkyline.jpg")',
          'background-size': 'cover'})


@app_flask.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


@app_flask.route('/main', methods=['POST', 'GET'])
def main():
    if not g.user:
        return redirect(url_for('login'))

    flist = []

    if request.method == "POST":
        bed = int(request.form["bed"])
        bath = float(request.form["bath"])
        floor = float(request.form["floor"])
        grade = int(request.form["grade"].split('.')[0])
        view = int(request.form["view"].split()[0])
        waterfront_str = request.form["waterfront"]
        if waterfront_str == 'No':
            waterfront = 0
        else:
            waterfront = 1
        sqftliving = int(request.form["sqftliving"])
        sqftbsmt = int(request.form["sqftbsmt"])
        sqftabove = sqftliving - sqftbsmt
        zipcode = int(request.form["zipcode"])

        # creates Random Forest Regression model based on user form inputs. Returns the model, a R2 score, and the
        # median of latitude and sqft_living15 based on user-input zipcode.
        model, score, latitude, sqftliving15 = create_model(zipcode)

        features_list = [bed, bath, sqftliving, floor, waterfront, view, grade, sqftabove, sqftbsmt, zipcode, latitude, sqftliving15]
        for feature in features_list:
            flist.append(feature)

        data = [flist]
        df = pd.DataFrame(data,
                          columns=['bedrooms', 'bathrooms', 'sqft_living', 'floors', 'waterfront', 'view', 'grade',
                                   'sqft_above', 'sqft_basement', 'zipcode', 'lat', 'sqft_living15'])

        session['est'] = f'${model.predict(df)[0]:,.2f}'
        session['score'] = f'{score * 100:.2f}%'

        return redirect(url_for('estimate'))

    else:
        return render_template('main.html', zipcode_list=zipcode_list)


@app_flask.route('/estimate', methods=['POST', 'GET'])
def estimate():
    if not g.user:
        return redirect(url_for('login'))

    est = session.get('est', None)
    score = session.get('score', None)

    return render_template('estimate.html', est=est, sc=score)


# Submits user's inquiry and contact information to a server file
@app_flask.route("/inquiry", methods=["POST"])
def inquiry():
    est = session.get('est', None)
    score = session.get('score', None)
    if session['inquiry_submitted']:
        error = 'Inquiry already submitted for this session.'
        return render_template('estimate.html', error=error, est=est, sc=score)
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    email = request.form['email']
    if not first_name or not last_name or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        error = 'Invalid contact information. Please try again.'
        return render_template('estimate.html', error=error, est=est, sc=score)
    with open('inquiries.txt', 'a') as f:
        f.write(str(str(datetime.datetime.now()) + ', ' + first_name + ', ' + last_name + ', ' + email + ', ' + est + ', ' + score + '\n'))
        session['inquiry_submitted'] = True
    correct = 'Inquiry has been successfully submitted!'
    return render_template('estimate.html', correct=correct, est=est, sc=score)


# Submits user's feedback data to a server file
@app_flask.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if not g.user:
        return redirect(url_for('login'))
    if session['feedback_submitted']:
        return redirect(url_for('main'))
    if request.method == 'POST':
        if session['feedback_submitted']:
            return redirect(url_for('main'))
        radio1 = request.form['group1']
        radio2 = request.form['group2']
        radio3 = request.form['group3']
        radio4 = request.form['group4']
        radio5 = request.form['group5']
        comments = request.form['comments']
        if not radio1 or not radio2 or not radio3 or not radio4 or not radio5:
            message = 'Please answer all 5 survey questions before submitting.'
            return render_template('feedback.html', message=message)
        with open('feedback.txt', 'a') as f:
            f.write(str(str(datetime.datetime.now()) + ', ' + radio1 + ', ' + radio2 + ', ' + radio3 + ', ' + radio4 +
                        ', ' + radio5 + ', ' + comments + '\n'))
        message = 'Feedback has been successfully submitted!'
        session['feedback_submitted'] = True
        return render_template('feedback.html', message=message)
    return render_template('feedback.html')


@app_flask.route('/visual')
def visual():
    if not g.user:
        return redirect(url_for('login'))
    if __name__ == '__main__':
        app_dash.run_server(debug=False)


@app_flask.route('/', methods=['POST', 'GET'])
def login():
    session.clear()
    error = ''
    if request.method == 'POST':
        session.pop('user_id', None)  # initially removes user from session if user attempts to log in again

        username = request.form['username']
        password = request.form['password']

        same_name_list = []

        for x in users:
            if x.username == username:
                same_name_list.append(x)
        if same_name_list:
            user = same_name_list[0]

            if user and user.password == password:
                session['user_id'] = user.id
                session['feedback_submitted'] = False
                session['inquiry_submitted'] = False
                return redirect(url_for('main'))

        error = 'Invalid Credentials. Please try again.'
        return render_template('login.html', error=error)

    return render_template('login.html', error=error)


# added port # to sync up with heroku web servers (heroku uses 33507 (or 5000) for flask applications)
port = int(os.environ.get('PORT', 5000))
if __name__ == '__main__':
    app_flask.run(host='0.0.0.0', port=port)

# # Sets up local server for testing the application. ~~~Comment out before deploying to production server.~~~
# if __name__ == '__main__':
#     app_flask.run(debug=True)
