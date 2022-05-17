from board.forms.client_form import ClientForm
from board.models import Country
from django.shortcuts import redirect, render
from django.views import View
from library.utils.auth import credentials
from library.utils.decorators import auth_check
from library.utils.logs import userlog
from library.utils.output_handle import general_valid_output
from slugify import slugify


class LabelsClientsFormView(View):
    @auth_check
    def dispatch(self, *args, **kwargs):
        userlog(self.request)
        return super().dispatch(self.request, *args, **kwargs)

    @auth_check
    def get(self, *args, **kwargs):
        # dropdown menu type
        countries = Country.objects.filter(
            cou_status=True
        ).order_by(
            'cou_name'
        ).values(
            'id',
            'cou_name',
        )

        # set initial context
        context = {
            'countries': countries,
        }

        # set messages, if applicable
        if 'success' in self.request.session:
            context['success'] = self.request.session.get('success')
            del self.request.session['success']
        elif 'error' in self.request.session:
            context['error'] = self.request.session.get('error')
            del self.request.session['error']

        return render(
            request=self.request,
            template_name='board/pages/labels_clients_form.html',
            context=context
        )

    @auth_check
    def post(self, *args, **kwargs):
        # update request to add user
        request_form = {}
        request_form['user'] = credentials(self.request.session['auth'], 'whoami')  # noqa: E501
        request_form['cli_name'] = self.request.POST.get('client')
        request_form['state'] = self.request.POST.get('state')
        request_form['cli_city'] = self.request.POST.get('city')
        request_form['cli_email'] = self.request.POST.get('email')
        request_form['cli_phone'] = self.request.POST.get('phone')
        request_form['cli_responsible'] = self.request.POST.get('responsible')

        country = Country.objects.filter(
            cou_status=True
        ).extra(
            where=['MD5(id)=%s'],
            params=[self.request.POST.get('country')]
        ).values('id')[0]

        request_form['country'] = country.get('id')

        form = ClientForm(request_form)

        # check validation
        if form.is_valid():
            data = form.save(commit=False)

            # adding remaining data and saving
            data.cli_slug = slugify(
                str(request_form.get('country')) +
                str(request_form.get('state')) +
                credentials(
                    self.request.session['auth'], 'login'
                ) +
                data.cli_name
            )
            data.cli_status = True
            data.save()

            self.request.session['success'] = 'Client added successfully.'
        else:
            self.request.session['error'] = 'Invalid data, client not registered:'  # noqa: E501
            # handling error message to display
            if form.errors.get('cli_name'):
                self.request.session['error'] += general_valid_output(
                    str(form.errors.get('cli_name'))
                )
            if form.errors.get('cli_city'):
                self.request.session['error'] += general_valid_output(
                    str(form.errors.get('cli_city'))
                )
            if form.errors.get('cli_email'):
                self.request.session['error'] += general_valid_output(
                    str(form.errors.get('cli_email'))
                )
            if form.errors.get('cli_phone'):
                self.request.session['error'] += general_valid_output(
                    str(form.errors.get('cli_phone'))
                )
            if form.errors.get('cli_responsible'):
                self.request.session['error'] += general_valid_output(
                    str(form.errors.get('cli_responsible'))
                )
        return redirect('board:labels_clients_form')
