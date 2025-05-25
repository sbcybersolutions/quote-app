from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Quote
from . import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Pull straight from form (always str, or KeyError if missing)
        client_name     = request.form['client_name'].strip()
        project_name    = request.form['project_name'].strip()
        project_date_str = request.form['project_date']

        # Validate presence
        if not (client_name and project_name and project_date_str):
            flash("All fields are required.", "danger")
            return render_template(
                'index.html',
                client_name=client_name,
                project_name=project_name,
                project_date=project_date_str
            )

        # Parse the date
        try:
            project_date = datetime.strptime(project_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return render_template(
                'index.html',
                client_name=client_name,
                project_name=project_name,
                project_date=project_date_str
            )

        # Create and save the Quote record by setting attributes directly
        quote = Quote()
        quote.client_name  = client_name
        quote.project_name = project_name
        quote.project_date = project_date

        db.session.add(quote)
        db.session.commit()

        return redirect(url_for('main.confirmation', client=client_name))

    # GET
    return render_template('index.html')


@main.route('/confirmation')
def confirmation():
    client = request.args.get('client', '')
    return render_template('confirmation.html', client=client)
