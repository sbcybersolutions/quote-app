from flask import render_template, request, redirect, url_for, flash
from datetime import datetime
from app.models import Quote
from app import db
from . import main

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        client_name = request.form.get('client_name', '').strip()
        project_name = request.form.get('project_name', '').strip()
        project_date_str = request.form.get('project_date', '').strip()

        if not (client_name and project_name and project_date_str):
            flash("All fields are required.", "danger")
            return render_template(
                'index.html',
                client_name=client_name,
                project_name=project_name,
                project_date=project_date_str
            )

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

        quote = Quote(
            client_name=client_name, # type: ignore
            project_name=project_name, # type: ignore
            project_date=project_date # type: ignore
        )
        db.session.add(quote)
        db.session.commit()

        return redirect(url_for('main.confirmation', client=client_name, quote_id=quote.id))

    return render_template('index.html')

@main.route('/confirmation')
def confirmation():
    client = request.args.get('client', '')
    quote_id = request.args.get('quote_id', type=int)
    return render_template('confirmation.html', client=client, quote_id=quote_id)

