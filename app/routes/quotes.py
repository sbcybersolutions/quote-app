from flask import render_template, request, redirect, url_for, flash, jsonify
from app.models import Quote, QuoteItem, ProjectType, VideoType
from app import db
from . import main

@main.route('/quotes')
def quote_list():
    quotes = Quote.query.order_by(Quote.created_at.desc()).all()
    return render_template('quotes.html', quotes=quotes)

@main.route('/quote/<int:quote_id>')
def quote_detail(quote_id: int):
    quote = Quote.query.get_or_404(quote_id)
    return render_template('quote_detail.html', quote=quote)

@main.route('/quote/<int:quote_id>/add-item', methods=['GET', 'POST'])
def add_quote_item(quote_id: int):
    quote = Quote.query.get_or_404(quote_id)
    project_types = ProjectType.query.all()
    video_types = VideoType.query.all() # type: ignore

    if request.method == 'POST':
        project_type_id = request.form.get('project_type', '').strip()
        quantity = request.form.get('quantity', type=int)
        custom_label = request.form.get('custom_label', '').strip()
        video_type_id = request.form.get('video_type_id', type=int)
        video_seconds = request.form.get('video_seconds', type=int)

        if not project_type_id or not quantity or quantity <= 0:
            flash('Please select a project type and enter a valid quantity.', 'danger')
            return render_template('add_item.html', quote=quote, project_types=project_types, video_types=video_types)

        item = QuoteItem(  # type: ignore
            quote_id=quote.id, # type: ignore
            project_type_id=int(project_type_id), # type: ignore
            quantity=quantity, # type: ignore
            custom_label=custom_label or None, # type: ignore
            video_type_id=video_type_id if video_type_id else None, # type: ignore
            video_seconds=video_seconds if video_seconds is not None else None # type: ignore
)
        db.session.add(item)
        db.session.commit()

        return redirect(url_for('main.quote_detail', quote_id=quote.id))

    return render_template('add_item.html', quote=quote, project_types=project_types, video_types=video_types)

@main.route('/project-type/<int:project_type_id>/unit-cost')
def get_unit_cost(project_type_id):
    pt = ProjectType.query.get_or_404(project_type_id)
    unit_cost = sum(r.hours_per_unit * r.rate_per_hour for r in pt.resources)
    return jsonify({'unit_cost': round(unit_cost, 2)})
