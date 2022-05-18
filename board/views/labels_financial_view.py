import math
import os
from datetime import datetime

from board.forms.financial_form import FinancialForm
from board.models import Financial
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View
from library.utils.auth import credentials
from library.utils.decorators import auth_check
from library.utils.helper import paginator
from library.utils.logs import userlog
from library.utils.output_handle import general_valid_output
from slugify import slugify

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


class LabelsFinancialView(View):
    @auth_check
    def dispatch(self, *args, **kwargs):
        userlog(self.request)
        return super().dispatch(self.request, *args, **kwargs)

    @auth_check
    def get(self, *args, **kwargs):
        # Set offset and limit
        pg = int(self.request.GET.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT

        financial_all = Financial.objects.filter(
            Q(
                Q(fin_cost_center__icontains=self.request.GET.get('search', '')) |  # noqa: E501
                Q(fin_description__icontains=self.request.GET.get('search', '')) |  # noqa: E501
                Q(fin_bank_name__icontains=self.request.GET.get('search', '')) |  # noqa: E501
                Q(fin_bank_account__icontains=self.request.GET.get('search', ''))  # noqa: E501
            ),
            user=credentials(self.request.session['auth'], 'whoami'),
            fin_status=True,
        ).order_by(
            '-fin_type',
            'fin_cost_center',
            'fin_description',
            'fin_bank_name',
            'fin_bank_branch',
            'fin_bank_account',
        ).values(
            'fin_slug',
            'fin_cost_center',
            'fin_description',
            'fin_bank_name',
            'fin_bank_branch',
            'fin_bank_account',
            'fin_type',
            'fin_date_created',
        )

        # Appling type filters, if applicable
        if self.request.GET.get('type'):
            financial_all = financial_all.filter(
                fin_type=self.request.GET.get('type')
            )

        # Separate rows for exposure
        financial = financial_all[pg_offset:(pg_offset+PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(financial_all.count()/PG_LIMIT)

        # Set page range
        pg_range = paginator(pg, total_pages)

        # set initial context
        context = {
            'financial': financial,
            'filter': {
                'type': self.request.GET.get('type', ''),
                'search': self.request.GET.get('search', '')
            },
            'pages': {
                'pg': pg,
                'total_pg': total_pages,
                'pg_range': pg_range
            }
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
            template_name='board/pages/labels_financial.html',
            context=context
        )

    @auth_check
    def post(self, *args, **kwargs):
        match self.request.path:
            case '/board/labels/financial/edit/':
                # setting request form
                request_form = {}
                request_form['user'] = credentials(self.request.session['auth'], 'whoami')  # noqa: E501
                request_form['fin_cost_center'] = self.request.POST.get('cost_center')  # noqa: E501
                request_form['fin_description'] = self.request.POST.get('description')  # noqa: E501
                request_form['fin_bank_name'] = self.request.POST.get('bank')
                request_form['fin_bank_branch'] = self.request.POST.get('branch')  # noqa: E501
                request_form['fin_bank_account'] = self.request.POST.get('account')  # noqa: E501
                request_form['edit_financial'] = self.request.POST.get('edit_financial')  # noqa: E501

                # get existing financial label from database
                data = Financial.objects.filter(
                    fin_status=True
                ).extra(
                    where=['MD5(fin_slug)=%s'],
                    params=[request_form.get('edit_financial')]
                )[0]

                request_form['fin_type'] = data.fin_type

                form = FinancialForm(request_form)

                if form.is_valid():
                    # updating data and saving
                    if data.fin_type == 1:
                        data.fin_cost_center = form.cleaned_data.get('fin_cost_center')  # noqa: E501
                        data.fin_description = form.cleaned_data.get('fin_description')  # noqa: E501
                        data.fin_slug = slugify(
                            str(data.fin_type) +
                            credentials(
                                self.request.session['auth'], 'login'
                            ) +
                            data.fin_cost_center
                        )
                    else:
                        data.fin_bank_name = form.cleaned_data.get('fin_bank_name')  # noqa: E501
                        data.fin_bank_branch = form.cleaned_data.get('fin_bank_branch')  # noqa: E501
                        data.fin_bank_account = form.cleaned_data.get('fin_bank_account')  # noqa: E501
                        data.fin_slug = slugify(
                            str(data.fin_type) +
                            credentials(
                                self.request.session['auth'], 'login'
                            ) +
                            data.fin_bank_name +
                            str(data.fin_bank_branch) +
                            str(data.fin_bank_account)
                        )
                    data.save()
                    if data.fin_type == 1:
                        self.request.session['success'] = 'Cost center edited successfully.'  # noqa: E501
                    else:
                        self.request.session['success'] = 'Bank account edited successfully.'  # noqa: E501
                else:
                    if request_form.get('fin_type') == 1:
                        self.request.session['error'] = 'Invalid data, cost center not edited:'  # noqa: E501
                    else:
                        self.request.session['error'] = 'Invalid data, bank account not edited:'  # noqa: E501

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
                return redirect('board:labels_financial')

            case '/board/labels/financial/delete/':
                # get existing client from database
                data = Financial.objects.filter(
                    fin_status=True
                ).extra(
                    where=['MD5(fin_slug)=%s'],
                    params=[self.request.POST.get('del_financial')]
                )[0]

                # updating data and saving - for delete status = 0
                data.fin_slug = slugify(
                    datetime.now().strftime('%m/%d/%Y, %H:%M:%S') +
                    data.fin_slug
                )
                data.fin_status = False
                data.fin_date_deleted = datetime.now()
                data.save()

                if data.fin_type == 1:
                    self.request.session['success'] = 'Cost center removed successfully.'  # noqa: E501
                else:
                    self.request.session['success'] = 'Bank account removed successfully.'  # noqa: E501
                return redirect('board:labels_financial')
