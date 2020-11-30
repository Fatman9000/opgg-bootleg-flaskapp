import functools
from typing import Callable
from flask import session, flash, redirect

def requires_user(f: Callable) -> Callable:
      @functools.wraps(f)
      def decorated_function(*args, **kwargs):
            if not session.get('name'):
                  flash("You need to enter a User before seeing matches", "danger")
                  return redirect("/")
            return f(*args, **kwargs)
      return decorated_function