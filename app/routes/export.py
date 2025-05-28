import io
import shutil
import xlsxwriter
import pdfkit
from flask import send_file, make_response, render_template
from app.models import Quote
from app.routes import main

@main.route('/quote/<int:quote_id>/export/excel')
def export_quote_excel(quote_id):
    quote = Quote.query.get_or_404(quote_id)

    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output, {'in_memory': True})
    ws = wb.add_worksheet("Quote")

    ws.write_row(0, 0, ["Quote ID", quote.id])
    ws.write_row(1, 0, ["Client", quote.client_name])
    ws.write_row(2, 0, ["Project", quote.project_name])
    ws.write_row(3, 0, ["Project Date", quote.project_date.strftime("%Y-%m-%d")])
    ws.write_row(4, 0, ["Created At", quote.created_at.strftime("%Y-%m-%d %H:%M:%S")])

    headers = ["Project Label", "Quantity", "Unit Cost", "Total Cost"]
    start_row = 6
    for col, h in enumerate(headers):
        ws.write(start_row, col, h)

    for i, item in enumerate(quote.items, start=1):
        row = start_row + i
        ws.write(row, 0, item.label)
        ws.write(row, 1, item.quantity)
        ws.write(row, 2, item.unit_cost)
        ws.write(row, 3, item.total_cost)

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
    grand_total = sum(item.total_cost for item in quote.items)

    rendered = render_template('export_quote.html', quote=quote, grand_total=grand_total)

    wk_path = shutil.which('wkhtmltopdf')
    if not wk_path:
        raise RuntimeError("wkhtmltopdf executable not found in PATH")

    config = pdfkit.configuration(wkhtmltopdf=wk_path)
    options = {
        'enable-local-file-access': None,
        'load-error-handling': 'ignore',
        'print-media-type': None
    }

    pdf_bytes = pdfkit.from_string(rendered, False, configuration=config, options=options)

    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=quote_{quote.id}.pdf'
    return response