from flask import render_template, request, redirect, url_for, flash
from app.models import Quote, QuoteItem, ProjectType
from app import db
from . import main

@main.route('/quotes')
def quote_list():
    quotes = Quote.query.order_by(Quote.created_at.desc()).all()
    return render_template('quotes.html', quotes=quotes)

# Quote details route
@main.route('/quote/<int:quote_id>')
def quote_detail(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    return render_template('quote_detail.html', quote=quote)

# Add item to quote route
@main.route('/quote/<int:quote_id>/add-item', methods=['GET', 'POST'])
def add_quote_item(quote_id: int):
    quote = Quote.query.get_or_404(quote_id)
    project_types = ProjectType.query.all()

    if request.method == 'POST':
        project_type_id: str = request.form.get('project_type', '').strip()
        quantity: int = request.form.get('quantity', type=int) # type: ignore
        custom_label = request.form.get('custom_label', '').strip()

        if not project_type_id or not quantity or quantity <= 0:
            flash('Please select a project type and enter a valid quantity.', 'danger')
            return render_template('add_item.html', quote=quote, project_types=project_types)

        item = QuoteItem(
            quote_id=quote.id, # type: ignore
            project_type_id=int(project_type_id), # type: ignore # type: ignore
            quantity=quantity, # type: ignore
            custom_label=custom_label # type: ignore
        )
        db.session.add(item)
        db.session.commit()

        return redirect(url_for('main.quote_detail', quote_id=quote.id))

    return render_template('add_item.html', quote=quote, project_types=project_types)
