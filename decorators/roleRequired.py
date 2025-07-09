from flask import session, flash, redirect, url_for, request
from functools import wraps

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if "rfc" not in session:
                flash("Inicia sesión para continuar")
                return redirect(url_for("login.home"))

            if roles and session.get("rol") not in roles:
                flash("No tienes permisos para ver esa página, vuelve a iniciar sesión con una cuenta que si los tenga")
                return redirect(url_for("login.home"))

            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator
