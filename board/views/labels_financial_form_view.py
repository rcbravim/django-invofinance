from board.forms.financial_form import FinancialForm
from django.shortcuts import redirect, render
from django.views import View
from library.utils.auth import credentials
from library.utils.decorators import auth_check
from library.utils.logs import userlog
from library.utils.output_handle import general_valid_output
from slugify import slugify


class LabelsFinancialFormView(View):
    @auth_check
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
            template_name='board/pages/labels_financial_form.html',
            context=context
        )

    @auth_check
    def post(self, *args, **kwargs):
        # update request to add user
        request_form = {}
        request_form['user'] = credentials(self.request.session['auth'], 'whoami')  # noqa: E501
        request_form['fin_cost_center'] = self.request.POST.get('cost_center')
        request_form['fin_description'] = self.request.POST.get('description')
        request_form['fin_bank_name'] = self.request.POST.get('bank')
        request_form['fin_bank_branch'] = self.request.POST.get('branch')
        request_form['fin_bank_account'] = self.request.POST.get('account')
        request_form['fin_type'] = 1 if self.request.POST.get('label_type') == 'CC' else 2  # noqa: E501

        form = FinancialForm(request_form)

        # check validation
        if form.is_valid():
            data = form.save(commit=False)

            # adding remaining data and saving
            if data.fin_type == 1:
                data.fin_slug = slugify(
                    str(data.fin_type) +
                    credentials(
                        self.request.session['auth'], 'login'
                    ) +
                    data.fin_cost_center
                )
            else:
                data.fin_slug = slugify(
                    str(data.fin_type) +
                    credentials(
                        self.request.session['auth'], 'login'
                    ) +
                    data.fin_bank_name +
                    str(data.fin_bank_branch) +
                    str(data.fin_bank_account)
                )
            data.fin_status = True
            data.save()

            if data.fin_type == 1:
                self.request.session['success'] = 'Cost center added successfully.'  # noqa: E501
            else:
                self.request.session['success'] = 'Bank account added successfully.'  # noqa: E501
        else:
            if request_form.get('fin_type') == 1:
                self.request.session['error'] = 'Invalid data, cost center not registered:'  # noqa: E501
            else:
                self.request.session['error'] = 'Invalid data, bank account not registered:'  # noqa: E501

            # handling error message to display
            if form.errors.get('fin_cost_center'):
                self.request.session['error'] += general_valid_output(
                    str(form.errors.get('fin_cost_center'))
                )
            if form.errors.get('fin_description'):
                self.request.session['error'] += general_valid_output(
                    str(form.errors.get('fin_description'))
                )
            if form.errors.get('fin_bank_name'):
                self.request.session['error'] += general_valid_output(
                    str(form.errors.get('fin_bank_name'))
                )
            if form.errors.get('fin_bank_branch'):
                self.request.session['error'] += general_valid_output(
                    str(form.errors.get('fin_bank_branch'))
                )
            if form.errors.get('fin_bank_account'):
                self.request.session['error'] += general_valid_output(
                    str(form.errors.get('fin_bank_account'))
                )
        return redirect('board:labels_financial_form')
