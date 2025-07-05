# middleware.py

import datetime
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return
        
        now = datetime.datetime.now()
        last_activity = request.session.get('last_activity', now.strftime("%Y-%m-%d %H:%M:%S.%f"))
        elapsed_time = (now - datetime.datetime.strptime(last_activity, "%Y-%m-%d %H:%M:%S.%f")).total_seconds()
        
        if elapsed_time > settings.SESSION_COOKIE_AGE:
            from django.contrib.auth import logout
            logout(request)
            messages.info(request, "You have been logged out due to inactivity.")
            return redirect('/')  
        
        request.session['last_activity'] = now.strftime("%Y-%m-%d %H:%M:%S.%f")
