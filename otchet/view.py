from flask import render_template


def view(table_name, string):
    if len(string) > 0:
        return render_template(table_name, item = string)
    else:
        return 'Информация не найдена'