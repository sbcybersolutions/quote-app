from flask import Blueprint, render_template, request, redirect, url_for

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        client_name = request.form.get('client_name')
        project_name = request.form.get('project_name')
        project_date = request.form.get('project_date')

        print(f"Client: {client_name}, Project: {project_name}, Date: {project_date}")

        # Later: save to DB or session
        return redirect(url_for('main.confirmation', client=client_name))

    return render_template('index.html')


@main.route('/confirmation')
def confirmation():
    client = request.args.get('client')
    return render_template('confirmation.html', client=client)


