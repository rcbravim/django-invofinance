from board.forms.profile_form import ProfileForm
from django.shortcuts import redirect, render
from django.views import View
from home.models import User, UserLog
from library.utils.auth import credentials
from library.utils.decorators import auth_check
from library.utils.helper import hash_gen
from library.utils.logs import userlog


class ProfileView(View):
    @auth_check
    def dispatch(self, *args, **kwargs):
        userlog(self.request)
        return super().dispatch(self.request, *args, **kwargs)

    @auth_check
    def get(self, *args, **kwargs):
        if 'password' in self.request.session:
            del self.request.session['password']

        session_login = UserLog.objects.filter(
            user=credentials(self.request.session['auth'], 'whoami'),
            log_risk_level=1,
        ).order_by(
            '-log_date_created'
        ).values(
            'log_date_created',
            'log_ip_address',
            'log_ip_country',
            'log_ip_country_flag'
        )[0:5]

        context = {
            'session': session_login
        }

        if 'success' in self.request.session:
            context['success'] = self.request.session.get('success')
            del self.request.session['success']
        elif 'error' in self.request.session:
            context['error'] = self.request.session.get('error')
            del self.request.session['error']

        return render(
            request=self.request,
            template_name='board/pages/profile.html',
            context=context
        )

    @auth_check
    def post(self, *args, **kwargs):
        # update request to add user
        request_form = {}
        request_form['use_password'] = self.request.POST.get('password')

        form = ProfileForm(request_form)

        # check validation
        if form.is_valid():
            exists = User.objects.filter(
                id=credentials(self.request.session['auth'], 'whoami'),
                use_password=hash_gen(form.cleaned_data.get('use_password')),
                use_status=True
            ).exists()

            if exists:
                self.request.session['password'] = {
                    'auth': True,
                    'attempt': 1
                }
                return redirect('board:password')
            else:
                self.request.session['error'] = 'Incorrect password.'
                return redirect('board:profile')
        else:
            self.request.session['error'] = 'Invalid password.'
            return redirect('board:profile')
