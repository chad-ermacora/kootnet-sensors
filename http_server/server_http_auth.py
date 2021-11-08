"""
    KootNet Sensors is a collection of programs and scripts to deploy,
    interact with, and collect readings from various Sensors.
    Copyright (C) 2018  Chad Ermacora  chad.ermacora@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from datetime import datetime
from flask import session, redirect
from operations_modules import app_cached_variables

auth_error_msg_contains = '<form class="pure-form" method="POST" action="/atpro/login">'


class CreateLoginManager:
    @staticmethod
    def login_required(func):
        def secure_function(*args, **kwargs):
            if "user_id" in session and session['user_id'] in app_cached_variables.http_flask_login_session_ids:
                app_cached_variables.http_flask_login_session_ids[session['user_id']] = datetime.utcnow()
                return func(*args, **kwargs)
            return redirect("/atpro/login")
        secure_function.__name__ = func.__name__
        return secure_function


auth = CreateLoginManager()
