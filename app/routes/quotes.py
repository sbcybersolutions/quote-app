from flask import render_template
from app.models import Quote
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