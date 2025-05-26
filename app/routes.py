from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    send_file, make_response
)
from .models import Quote
from . import db
from datetime import datetime
import io, xlsxwriter, pdfkit

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

@main.route('/quote/<int:quote_id>/export/excel')
def export_quote_excel(quote_id):
    # Fetch the quote
    quote = Quote.query.get_or_404(quote_id)

    # Prepare in-memory workbook
    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output, {'in_memory': True})
    ws = wb.add_worksheet("Quote")

    # Metadata at the top
    ws.write_row(0, 0, ["Quote ID", quote.id])
    ws.write_row(1, 0, ["Client", quote.client_name])
    ws.write_row(2, 0, ["Project", quote.project_name])
    ws.write_row(3, 0, ["Project Date", quote.project_date.strftime("%Y-%m-%d")])
    ws.write_row(4, 0, ["Created At", quote.created_at.strftime("%Y-%m-%d %H:%M:%S")])

    # Headers for items table
    headers = ["Project Type", "Quantity", "Unit Cost", "Total Cost"]
    start_row = 6
    for col, h in enumerate(headers):
        ws.write(start_row, col, h)

    # Rows for each QuoteItem
    for i, item in enumerate(quote.items, start=1):
        row = start_row + i
        ws.write(row, 0, item.project_type.name)
        ws.write(row, 1, item.quantity)
        ws.write(row, 2, item.unit_cost)
        ws.write(row, 3, item.total_cost)

    # Grand total
    grand_total = sum(item.total_cost for item in quote.items)
    ws.write(start_row + len(quote.items) + 2, 2, "Grand Total")
    ws.write(start_row + len(quote.items) + 2, 3, grand_total)

    wb.close()
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=f"quote_{quote.id}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@main.route('/quote/<int:quote_id>/export/pdf')
def export_quote_pdf(quote_id):
    quote = Quote.query.get_or_404(quote_id)

    # Calculate grand total in Python
    grand_total = sum(item.total_cost for item in quote.items)

    # Render HTML template
    rendered = render_template(
        'export_quote.html',
        quote=quote,
        grand_total=grand_total
    )

    # Convert to PDF (requires wkhtmltopdf on PATH)
    pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers[
        'Content-Disposition'
    ] = f'attachment; filename=quote_{quote.id}.pdf'
    return response

@main.route('/quotes')
def quote_list():
    quotes = Quote.query.order_by(Quote.created_at.desc()).all()
    return render_template('quotes.html', quotes=quotes)