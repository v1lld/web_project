from flask import render_template

def view(sentens):
    length = len(sentens['result'])
    print(length)
    print(sentens['result'])
    if length > 0:
        return render_template('table_out.html', item = sentens)
    else:
        return render_template('eror.html')