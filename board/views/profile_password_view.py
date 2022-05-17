import os

from board.forms.profile_password_form import ProfilePasswordForm
from django.shortcuts import redirect, render
from django.views import View
from home.models import User
from library.utils.auth import credentials
from library.utils.decorators import auth_check
from library.utils.helper import hash_gen
from library.utils.logs import userlog
from library.utils.output_handle import password_valid_output

MAX_ATTEMPTS = int(os.environ.get('MAX_ATTEMPTS', 3))


class ProfilePasswordView(View):
    @auth_check
    def dispatch(self, *args, **kwargs):
        userlog(self.request)
        return super().dispatch(self.request, *args, **kwargs)

    @auth_check
    def get(self, *args, **kwargs):
        context = {}
        if 'password' in self.request.session:
            if self.request.session['password']['attempt'] <= MAX_ATTEMPTS:
                if 'error' in self.request.session:
                    context['error'] = self.request.session.get('error')
                    del self.request.session['error']

                return render(
                    request=self.request,
                    template_name='board/pages/profile_password.html',
                    context=context
                )
            else:
                self.request.session['error'] = 'You have reached the ' \
                    'maximum number of attempts, please log in and try again.'
                return redirect('board:profile')
        else:
            self.request.session['error'] = 'You are not authorized to access this page.'  # noqa: E501
            return redirect('board:profile')

    @auth_check
    def post(self, *args, **kwargs):
        # update request to add user
        request_form = {}
        request_form['use_password'] = self.request.POST.get('password')
        request_form['password_confirmation'] = self.request.POST.get('password_confirmation')  # noqa: E501

        form = ProfilePasswordForm(request_form)

        # check validation
        if form.is_valid():
            data = User.objects.filter(
                id=credentials(self.request.session['auth'], 'whoami'),
                use_status=True
            )[0]

            # updating data and saving
            data.use_password = hash_gen(form.cleaned_data.get('use_password'))
            data.save()

            self.request.session['success'] = 'Password edited successfully.'
            return redirect('board:profile')
        else:
            self.request.session['password']['attempt'] += 1

            self.request.session['error'] = 'Invalid data, password not edited:'  # noqa: E501
            # handling error message to display
            self.request.session['error'] += password_valid_output(
                str(form.errors.get('use_password'))
            )
            return redirect('board:password')
