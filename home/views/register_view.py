import os
import random
import string

from django.shortcuts import redirect, render
from django.views import View
from home.forms.resgiter_form import RegisterForm
from home.models import User
from library.utils.decorators import auth_check
from library.utils.helper import hash_gen
from library.utils.logs import userlog
from library.utils.output_handle import (email_valid_output,
                                         password_valid_output)

MAX_ATTEMPTS = int(os.getenv('MAX_ATTEMPTS', 3))


class RegisterView(View):
    def dispatch(self, *args, **kwargs):
        userlog(self.request)
        return super().dispatch(self.request, *args, **kwargs)

    @auth_check
    def get(self, *args, **kwargs):
        match self.request.path:
            case '/register/':
                context = {'stage': 'one'}
                if 'error' in self.request.session:
                    context['error'] = self.request.session.get('error')
                    del self.request.session['error']
                elif 'stage' in self.request.session:
                    context['attempts'] = MAX_ATTEMPTS - self.request.session.get('counter') + 1  # noqa: E501
                    context['email'] = self.request.session.get('email')
                    context['stage'] = self.request.session.get('stage')

                    if 'modal' in self.request.session:
                        context['modal'] = self.request.session.get('modal')
                        del self.request.session['modal']
                    if 'email-code' not in self.request.session:
                        self.request.session['email-code'] = ''.join(random.choices(string.digits, k=4))  # noqa: E501
                        # print(self.request.session.__dict__)
                        # EMAIL SENDER
                return render(
                    request=self.request,
                    template_name='home/pages/register.html',
                    context=context
                )
            case '/register/failed/':
                try:
                    user = User.objects.filter(
                        use_login=self.request.session['email'],
                        use_password=self.request.session['password'],
                        use_status=True
                    )[0]
                    user.use_status = False
                    user.save()

                    del self.request.session['counter']
                    del self.request.session['email']
                    del self.request.session['email-code']
                    del self.request.session['password']
                    del self.request.session['stage']
                    return render(
                        request=self.request,
                        template_name='home/pages/failed.html'
                    )
                except Exception:
                    return redirect('home:404')

    @auth_check
    def post(self, *args, **kwargs):
        match self.request.path:
            case '/register/new/':
                form = RegisterForm(self.request.POST)
                if form.is_valid():
                    data = form.save(commit=False)
                    data.use_password = hash_gen(data.use_password)
                    data.use_status = True
                    data.save()

                    self.request.session['counter'] = 1
                    self.request.session['email'] = data.use_login
                    self.request.session['password'] = data.use_password
                    self.request.session['stage'] = 'two'
                else:
                    self.request.session['error'] = 'Invalid data, user not registered:'  # noqa: E501

                    errors = ''
                    if form.errors.get('use_login'):
                        errors += email_valid_output(
                            str(form.errors.get('use_login'))
                        )
                    if form.errors.get('use_password'):
                        errors += password_valid_output(
                            str(form.errors.get('use_password'))
                        )
                    self.request.session['error'] += errors
                return redirect('home:register')

            case '/register/verify/':
                email_code = self.request.POST['digit1'] + \
                    self.request.POST['digit2'] + self.request.POST['digit3'] \
                    + self.request.POST['digit4']

                if self.request.session['email-code'] == email_code:

                    user = User.objects.filter(
                        use_login=self.request.session['email'],
                        use_password=self.request.session['password'],
                        use_status=True
                    )[0]
                    user.use_is_valid = True
                    user.save()

                    del self.request.session['counter']
                    del self.request.session['email']
                    del self.request.session['email-code']
                    del self.request.session['password']
                    del self.request.session['stage']

                    self.request.session['success'] = 'User registered successfully!'  # noqa: E501
                    return redirect('home:index')
                else:
                    if self.request.session['counter'] < MAX_ATTEMPTS:
                        self.request.session['counter'] += 1
                        return redirect('home:register')
                    else:
                        return redirect('home:register_failed')
