"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    
    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/register")
def register_form():
    """Display register form."""

    

    return render_template("register_form.html")

@app.route('/register', methods=["POST"])
def register_process():
    """Process form."""

    password = request.form.get("password")
    user_email = request.form.get("email")

    if User.query.filter_by(email=user_email).first() is None:

        user = User(email=user_email,
                    password=password)


        db.session.add(user)
        db.session.commit()

    else:
        flash('You already have an account.')

    return redirect('/')

@app.route('/login')
def login_form():
    """Display login form."""

    return render_template("login_form.html")

@app.route('/login', methods=["POST"])
def login_in_process():
    """Login in process."""

    user_password = request.form.get("password")
    user_email = request.form.get("email")

    if User.query.filter_by(email=user_email, password=user_password).first():
        user_id = User.query.filter_by(email=user_email).first().user_id
        flash('Logged in.')
        session['user_email'] = user_email

        return redirect('/users/{}'.format(user_id))
    else:
        flash("Wrong email or password!")
        return redirect("/login")

@app.route('/logout')
def log_out_process():
    """Log out process."""


    del session['user_email']
    flash('Logged out.')

    return redirect('/')

@app.route('/users/<user_id>')
def user_details(user_id):
    """Give user details."""

    user = User.query.filter_by(user_id=user_id).first()
    # movies = Movie.query.filter_by(u)

    return render_template('user_page.html',
                            user=user)


@app.route('/movieslist')
def movie_list():
    """Display movie list."""

    movies = Movie.query.order_by('title').all()

    return render_template('movie_list.html',
                            movies=movies)

@app.route('/movieslist/<title>')
def show_movie_details(title):
    """Show movie details."""

    movie = Movie.query.filter_by(title=title).first()

    ratings = Rating.query.filter_by(movie_id=movie.movie_id).all()

    return render_template('movie_details.html',
                            movie=movie,
                            ratings=ratings)

@app.route('/processrating', methods=["POST"])
def process_rating():
    """Add/Update rating."""

    score = request.form.get('score')
    movie = request.form.get('movie')

    rating = Ratings.query.filter_by(movie_id == movie and user_id == session["user_id"]).first()
    if rating:
        rating.score = score
    else:
        rating = Rating(score=score,
                       movie_id=movie_id,
                       user_id=user_id)
        db.session.add(rating)
    db.session.commit()

    return redirect('/movieslist')



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
