from datetime import datetime, timedelta

from django.shortcuts import redirect, render
from django.views import View
from home.forms.index_form import IndexForm
from home.models import User
from library.utils.auth import auth
from library.utils.decorators import auth_check
from library.utils.helper import hash_gen
from library.utils.logs import userlog


class IndexView(View):
    def dispatch(self, *args, **kwargs):
        userlog(self.request)
        return super().dispatch(self.request, *args, **kwargs)

    @auth_check
    def get(self, *args, **kwargs):
        context = {}
        if 'success' in self.request.session:
            context['success'] = self.request.session.get('success')
            del self.request.session['success']
        elif 'error' in self.request.session:
            context['error'] = self.request.session.get('error')
            del self.request.session['error']
        return render(
            request=self.request,
            template_name='home/pages/index.html',
            context=context
        )

    @auth_check
    def post(self, *args, **kwargs):
        form = IndexForm(self.request.POST)
        if form.is_valid():
            try:
                valid = User.objects.filter(
                    use_login=form.cleaned_data.get('use_login'),
                    use_password=hash_gen(form.cleaned_data.get('use_password')),  # noqa: E501
                    use_status=True
                )[0]

                if valid.use_is_valid is True:
                    payload = {
                        'whoami': valid.id,
                        'login': valid.use_login,
                        'manager': valid.use_is_manager,
                        'iss': datetime.now().strftime('%s'),
                        'exp': (datetime.now() + timedelta(minutes=30)).strftime('%s')  # noqa: E501
                    }
                    self.request.session['auth'] = auth(payload=payload)
                    self.request.session['success'] = 'You are logged in.'

                    userlog(self.request, risk=1)

                    if valid.use_is_manager is True:
                        return redirect('manager:index')
                    else:
                        return redirect('board:index')
                else:
                    self.request.session['counter'] = 1
                    self.request.session['email'] = valid.use_login
                    self.request.session['password'] = valid.use_password
                    self.request.session['stage'] = 'two'
                    self.request.session['modal'] = True
                    if 'email-code' in self.request.session:
                        del self.request.session['email-code']
                    return redirect('home:register')
            except Exception:
                self.request.session['error'] = 'Incorrect email or password.'
                return redirect('home:index')
        else:
            self.request.session['error'] = 'Invalid email or password.'
            return redirect('home:index')
