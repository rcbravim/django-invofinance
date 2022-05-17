from django.shortcuts import redirect
from django.views import View
from library.utils.logs import userlog


class LogoutView(View):
    def dispatch(self, *args, **kwargs):
        userlog(self.request)
        return super().dispatch(self.request, *args, **kwargs)

    def get(self, *args, **kwargs):
        del self.request.session['auth']
        return redirect('home:index')
