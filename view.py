from flask import render_template ,session


def view(table_name):
    if 'vgroup' in session:
        return render_template(table_name, message=session['vgroup'])
    else:
        return render_template(table_name)