from flask import Blueprint, render_template, current_app, request, session, redirect
from functools import wraps


def group_validation(config: dict):
    endpoint_app = request.endpoint.split('.')[0]
    endpoint_appp = request.endpoint.split('.')[-1]
    if 'vgroup' in session:
        group = session['vgroup']
        if group in config and endpoint_app in config[group]:
            return True
        elif group in config and endpoint_appp in config[group]:
            return True
    return False

def login_required():
    def login_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            is_login = session.get("vgroup", False)
            if is_login:
                if group_validation(current_app.config["access_config"]):
                    result = func(*args, **kwargs)
                    return result
                else:
                    return "нет доступа"
            else:
                return redirect("/log/login/")
        return wrapper
    return login_wrapper



