from flask import render_template
from app import app, db


@app.errorhandler(404)  # the arhument provided is the http status code
def not_found_error(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # clean up broken transactions
    return render_template("500.html"), 500
