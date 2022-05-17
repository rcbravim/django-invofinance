import json
import math
import os
from contextlib import suppress
from datetime import datetime

from board.forms.index_form import AnalyticForm, IndexForm
from board.models import (Analytic, Beneficiary, Category, Client, Financial,
                          Release, SubCategory)
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.views import View
from library.utils.auth import credentials
from library.utils.decorators import auth_check
from library.utils.helper import paginator
from library.utils.logs import userlog
from library.utils.output_handle import general_valid_output
from slugify import slugify

PG_LIMIT = int(os.environ.get('PG_LIMIT', 25))


class BoardIndexView(View):
    @auth_check
    def dispatch(self, *args, **kwargs):
        userlog(self.request)
        return super().dispatch(self.request, *args, **kwargs)

    @auth_check
    def get(self, *args, **kwargs):
        # Set offset and limit
        pg = int(self.request.GET.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT

        if self.request.GET.get('m'):
            date = f'{self.request.GET.get("y")}-{self.request.GET.get("m")}'
            displayed = datetime.strptime(date, '%Y-%m')
        else:
            displayed = datetime.now()

        # Select all rows
        entries_all = Release.objects.select_related(
            'subcategory'
        ).filter(
            user=credentials(self.request.session['auth'], 'whoami'),
            rel_status=True,
        ).extra(
            where=['MONTH(rel_entry_date)=%s and YEAR(rel_entry_date)=%s'],
            params=[displayed.strftime('%m'), displayed.strftime('%Y')]
        ).order_by(
            '-rel_sqn',
        ).values(
            'rel_entry_date',
            'rel_slug',
            'subcategory__category__cat_name',
            'subcategory__category__cat_type',
            'subcategory__sub_name',
            'rel_gen_status',
            'rel_amount',
            'rel_monthly_balance',
            'rel_overall_balance'
        )

        # Separate rows for exposure
        entries = entries_all[pg_offset:(pg_offset+PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(entries_all.count()/PG_LIMIT)

        # Set page range
        pg_range = paginator(pg, total_pages)

        # Select options for new entry
        categories = Category.objects.filter(
            user_id=credentials(self.request.session['auth'], 'whoami'),
            cat_status=True
        ).order_by(
            'cat_name'
        ).values(
            'cat_slug',
            'cat_name'
        )

        beneficiaries = Beneficiary.objects.select_related(
            'beneficiary_category'
        ).filter(
            user_id=credentials(self.request.session['auth'], 'whoami'),
            ben_status=True
        ).order_by(
            'beneficiary_category__cat_description',
            'ben_name'
        ).values(
            'ben_slug',
            'ben_name',
            'beneficiary_category__cat_description'
        )

        clients = Client.objects.filter(
            user_id=credentials(self.request.session['auth'], 'whoami'),
            cli_status=True
        ).order_by(
            'cli_name'
        ).values(
            'cli_slug',
            'cli_name'
        )

        cost_centers = Financial.objects.filter(
            user_id=credentials(self.request.session['auth'], 'whoami'),
            fin_bank_name__isnull=True,
            fin_status=True
        ).order_by(
            'fin_cost_center'
        ).values(
            'fin_slug',
            'fin_cost_center'
        )

        accounts = Financial.objects.filter(
            user_id=credentials(self.request.session['auth'], 'whoami'),
            fin_cost_center__isnull=True,
            fin_status=True
        ).order_by(
            'fin_bank_name'
        ).values(
            'fin_slug',
            'fin_bank_name',
            'fin_bank_branch',
            'fin_bank_account'
        )

        analytic = Analytic.objects.filter(
            user_id=credentials(self.request.session['auth'], 'whoami'),
            ana_cycle=f'{displayed.strftime("%Y-%m")}-01',
            ana_status=True
        ).values('ana_json')
        past = False

        if not analytic:
            analytic = Analytic.objects.filter(
                user_id=credentials(self.request.session['auth'], 'whoami'),
                ana_cycle__lt=f'{displayed.strftime("%Y-%m")}-01',
                ana_status=True
            ).order_by(
                '-ana_cycle'
            ).values('ana_json')
            past = True

        context = {
            'entries': entries,
            'categories': categories,
            'beneficiaries': beneficiaries,
            'clients': clients,
            'cost_centers': cost_centers,
            'accounts': accounts,
            'analytic': json.loads(analytic[0].get('ana_json')) if analytic else None,  # noqa: E501
            'past': past,
            'filter': {
                'displayed': displayed.strftime('%b.%Y'),
                'month': self.request.GET.get('m'),
                'year': self.request.GET.get('y')
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
            template_name='board/pages/index.html',
            context=context
        )

    @auth_check
    def post(self, *args, **kwargs):
        match self.request.path:
            case '/board/index/new/':
                # update request to add user
                request_form = {}
                request_form['user'] = credentials(self.request.session['auth'], 'whoami')  # noqa: E501
                request_form['rel_entry_date'] = self.request.POST.get('entry_date')  # noqa: E501
                request_form['subcategory'] = self.request.POST.get('subcategory')  # noqa: E501
                request_form['rel_description'] = self.request.POST.get('description')  # noqa: E501
                request_form['beneficiary'] = self.request.POST.get('beneficiary')  # noqa: E501
                request_form['client'] = self.request.POST.get('client')
                request_form['financial_cost_center'] = self.request.POST.get('cost_center')  # noqa: E501
                request_form['rel_gen_status'] = self.request.POST.get('condition')  # noqa: E501
                request_form['financial_account'] = self.request.POST.get('account')  # noqa: E501
                request_form['rel_amount'] = self._cleaning_number_string(self.request.POST.get('amount'))  # noqa: E501

                form = IndexForm(request_form)

                # check validation
                if form.is_valid():
                    data = form.save(commit=False)

                    # getting the ID's of each field
                    try:
                        data.subcategory = SubCategory.objects.get(
                            id=SubCategory.objects.filter(
                                sub_status=True
                            ).extra(
                                where=['MD5(sub_slug)=%s'],
                                params=[form.data.get('subcategory')]
                            ).values('id')[0]['id']
                        )
                    except Exception as err:
                        return self._error_exception(err)

                    try:
                        data.beneficiary = Beneficiary.objects.get(
                            id=Beneficiary.objects.filter(
                                user=form.cleaned_data.get('user'),
                                ben_status=True
                            ).extra(
                                where=['MD5(ben_slug)=%s'],
                                params=[form.data.get('beneficiary')]
                            ).values('id')[0]['id']
                        )
                    except Exception as err:
                        return self._error_exception(err)

                    if form.data.get('client'):
                        try:
                            data.client = Client.objects.get(
                                id=Client.objects.filter(
                                    user=form.cleaned_data.get('user'),
                                    cli_status=True
                                ).extra(
                                    where=['MD5(cli_slug)=%s'],
                                    params=[form.data.get('client')]
                                ).values('id')[0]['id']
                            )
                        except Exception as err:
                            return self._error_exception(err)

                    if form.data.get('financial_cost_center'):
                        try:
                            data.financial_cost_center = Financial.objects.get(
                                id=Financial.objects.filter(
                                    user=form.cleaned_data.get('user'),
                                    fin_bank_name__isnull=True,
                                    fin_status=True
                                ).extra(
                                    where=['MD5(fin_slug)=%s'],
                                    params=[form.data.get('financial_cost_center')]  # noqa: E501
                                ).values('id')[0]['id']
                            )
                        except Exception as err:
                            return self._error_exception(err)

                    try:
                        data.financial_account = Financial.objects.get(
                            id=Financial.objects.filter(
                                user=form.cleaned_data.get('user'),
                                fin_cost_center__isnull=True,
                                fin_status=True
                            ).extra(
                                where=['MD5(fin_slug)=%s'],
                                params=[form.data.get('financial_account')]
                            ).values('id')[0]['id']
                        )
                    except Exception as err:
                        return self._error_exception(err)

                    # getting unique sequential number (SQN)
                    """ with suppress(Exception):
                        last_sqn = Release.objects.filter(
                            user=credentials(
                                self.request.session['auth'], 'whoami'
                            ),
                            rel_entry_date__gt=data.rel_entry_date,
                            rel_status=True,
                        ).order_by(
                            'rel_sqn'
                        ).values(
                            'rel_sqn',
                            'rel_monthly_balance',
                            'rel_overall_balance'
                        )[0]
                        data.rel_sqn = last_sqn['rel_sqn']

                    if data.rel_sqn is None: """
                    try:
                        last_sqn = Release.objects.filter(
                            user=credentials(
                                self.request.session['auth'], 'whoami'
                            ),
                            rel_entry_date__lte=data.rel_entry_date,
                            rel_status=True,
                        ).order_by(
                            '-rel_sqn'
                        ).values(
                            'rel_sqn',
                            'rel_monthly_balance',
                            'rel_overall_balance'
                        )[0]
                        data.rel_sqn = last_sqn['rel_sqn'] + 1
                    except Exception:
                        data.rel_sqn = 1

                    data.rel_monthly_balance, data.rel_overall_balance = self._balance_calculation(  # noqa: E501
                        amount=data.rel_amount,
                        date=data.rel_entry_date,
                        subcategory=form.data.get('subcategory'),
                        sqn=data.rel_sqn
                    )

                    # adding remaining data and saving
                    data.rel_slug = slugify(
                        datetime.now().strftime('%m/%d/%Y, %H:%M:%S') +
                        credentials(
                            self.request.session['auth'], 'login'
                        ) +
                        str(data.subcategory) +
                        str(data.rel_amount)
                    )
                    data.rel_status = True
                    data.save()

                    error = self._analytic_calculation(
                        date=data.rel_entry_date,
                        sqn=data.rel_sqn,
                        monthly_balance=data.rel_monthly_balance,
                        overall_balance=data.rel_overall_balance,
                        id=data.id
                    )
                    if error:
                        self.request.session['error'] = error
                    else:
                        self.request.session['success'] = 'New entry added successfully.'  # noqa: E501
                else:
                    self.request.session['error'] = 'Invalid data, new entry not registered:'  # noqa: E501
                    # handling error message to display
                    if form.errors.get('rel_description'):
                        self.request.session['error'] += general_valid_output(
                            str(form.errors.get('rel_description'))
                        )
                    if form.errors.get('rel_entry_date'):
                        self.request.session['error'] += general_valid_output(
                            str(form.errors.get('rel_entry_date'))
                        )
                    if form.errors.get('rel_amount'):
                        self.request.session['error'] += general_valid_output(
                            str(form.errors.get('rel_amount'))
                        )
                return redirect('board:index')
            case '/board/index/edit/':
                # setting request form
                request_form = {}
                request_form['user'] = credentials(self.request.session['auth'], 'whoami')  # noqa: E501
                request_form['rel_entry_date'] = self.request.POST.get('entry_date_edit')  # noqa: E501
                request_form['subcategory'] = self.request.POST.get('subcategory_edit')  # noqa: E501
                request_form['rel_description'] = self.request.POST.get('description_edit')  # noqa: E501
                request_form['beneficiary'] = self.request.POST.get('beneficiary_edit')  # noqa: E501
                request_form['client'] = self.request.POST.get('client_edit')
                request_form['financial_cost_center'] = self.request.POST.get('cost_center_edit')  # noqa: E501
                request_form['rel_gen_status'] = self.request.POST.get('condition_edit')  # noqa: E501
                request_form['financial_account'] = self.request.POST.get('account_edit')  # noqa: E501
                request_form['rel_amount'] = self._cleaning_number_string(self.request.POST.get('amount_edit'))  # noqa: E501
                request_form['edit_index'] = self.request.POST.get('edit_index')  # noqa: E501

                form = IndexForm(request_form)

                # check validation
                if form.is_valid():
                    # get existing beneficiary from database
                    data = Release.objects.filter(
                        rel_status=True
                    ).extra(
                        where=['MD5(rel_slug)=%s'],
                        params=[form.data.get('edit_index')]
                    )[0]
                    current_sqn = data.rel_sqn
                    current_entry_date = data.rel_entry_date

                    # getting the ID's of each field
                    try:
                        data.subcategory = SubCategory.objects.get(
                            id=SubCategory.objects.filter(
                                sub_status=True
                            ).extra(
                                where=['MD5(sub_slug)=%s'],
                                params=[form.data.get('subcategory')]
                            ).values('id')[0]['id']
                        )
                    except Exception as err:
                        return self._error_exception(err)

                    try:
                        data.beneficiary = Beneficiary.objects.get(
                            id=Beneficiary.objects.filter(
                                user=form.cleaned_data.get('user'),
                                ben_status=True
                            ).extra(
                                where=['MD5(ben_slug)=%s'],
                                params=[form.data.get('beneficiary')]
                            ).values('id')[0]['id']
                        )
                    except Exception as err:
                        return self._error_exception(err)

                    if form.data.get('client'):
                        try:
                            data.client = Client.objects.get(
                                id=Client.objects.filter(
                                    user=form.cleaned_data.get('user'),
                                    cli_status=True
                                ).extra(
                                    where=['MD5(cli_slug)=%s'],
                                    params=[form.data.get('client')]
                                ).values('id')[0]['id']
                            )
                        except Exception as err:
                            return self._error_exception(err)

                    if form.data.get('financial_cost_center'):
                        try:
                            data.financial_cost_center = Financial.objects.get(
                                id=Financial.objects.filter(
                                    user=form.cleaned_data.get('user'),
                                    fin_bank_name__isnull=True,
                                    fin_status=True
                                ).extra(
                                    where=['MD5(fin_slug)=%s'],
                                    params=[form.data.get('financial_cost_center')]  # noqa: E501
                                ).values('id')[0]['id']
                            )
                        except Exception as err:
                            return self._error_exception(err)

                    try:
                        data.financial_account = Financial.objects.get(
                            id=Financial.objects.filter(
                                user=form.cleaned_data.get('user'),
                                fin_cost_center__isnull=True,
                                fin_status=True
                            ).extra(
                                where=['MD5(fin_slug)=%s'],
                                params=[form.data.get('financial_account')]
                            ).values('id')[0]['id']
                        )
                    except Exception as err:
                        return self._error_exception(err)

                    # getting unique sequential number (SQN)
                    try:
                        last_sqn = Release.objects.filter(
                            user=credentials(
                                self.request.session['auth'], 'whoami'
                            ),
                            rel_entry_date__lte=form.cleaned_data.get('rel_entry_date'),  # noqa: E501
                            rel_status=True,
                        ).exclude(
                            id=data.id
                        ).order_by(
                            '-rel_sqn'
                        ).values(
                            'rel_sqn',
                            'rel_monthly_balance',
                            'rel_overall_balance'
                        )[0]
                        data.rel_sqn = last_sqn['rel_sqn'] + 1
                    except Exception:
                        data.rel_sqn = 1

                    data.rel_monthly_balance = data.rel_overall_balance = 0

                    # updating data and saving
                    data.rel_entry_date = form.cleaned_data.get('rel_entry_date')  # noqa: E501
                    data.rel_description = form.cleaned_data.get('rel_description')  # noqa: E501
                    data.rel_gen_status = form.cleaned_data.get('rel_gen_status')  # noqa: E501
                    data.rel_amount = form.cleaned_data.get('rel_amount')
                    data.rel_slug = slugify(
                        datetime.now().strftime('%m/%d/%Y, %H:%M:%S') +
                        credentials(
                            self.request.session['auth'], 'login'
                        ) +
                        str(data.subcategory) +
                        str(data.rel_amount)
                    )
                    data.save()

                    with suppress(Exception):
                        previous_entry = Release.objects.filter(
                            user=credentials(
                                self.request.session['auth'], 'whoami'
                            ),
                            rel_sqn__lte=(data.rel_sqn if data.rel_sqn < current_sqn else current_sqn) - 1,  # noqa: E501
                            rel_status=True,
                        ).values(
                            'rel_monthly_balance',
                            'rel_overall_balance'
                        )[0]
                        data.rel_monthly_balance = previous_entry.get('rel_monthly_balance')  # noqa: E501
                        data.rel_overall_balance = previous_entry.get('rel_overall_balance')  # noqa: E501

                    error = self._analytic_calculation(
                        date=data.rel_entry_date if data.rel_entry_date < current_entry_date else current_entry_date,  # noqa: E501
                        sqn=data.rel_sqn if data.rel_sqn < current_sqn else current_sqn,  # noqa: E501
                        monthly_balance=data.rel_monthly_balance,
                        overall_balance=data.rel_overall_balance
                    )
                    if error:
                        self.request.session['error'] = error
                    else:
                        self.request.session['success'] = 'Entry edited successfully.'  # noqa: E501
                else:
                    self.request.session['error'] = 'Invalid data, entry not edited:'  # noqa: E501
                    # handling error message to display
                    if form.errors.get('rel_description'):
                        self.request.session['error'] += general_valid_output(
                            str(form.errors.get('rel_description'))
                        )
                    if form.errors.get('rel_entry_date'):
                        self.request.session['error'] += general_valid_output(
                            str(form.errors.get('rel_entry_date'))
                        )
                    if form.errors.get('rel_amount'):
                        self.request.session['error'] += general_valid_output(
                            str(form.errors.get('rel_amount'))
                        )
                return redirect('board:index')
            case '/board/index/delete/':
                # get existing entry from database
                data = Release.objects.filter(
                    rel_status=True
                ).extra(
                    where=['MD5(rel_slug)=%s'],
                    params=[self.request.POST.get('del_index')]
                )[0]

                # updating data and saving - for delete status = 0
                data.rel_slug = slugify(
                    datetime.now().strftime('%m/%d/%Y, %H:%M:%S') +
                    data.rel_slug
                )
                data.rel_status = False
                data.rel_date_deleted = datetime.now()
                data.save()

                try:
                    last_sqn = Release.objects.filter(
                        user=credentials(
                            self.request.session['auth'], 'whoami'
                        ),
                        rel_sqn__lt=data.rel_sqn,
                        rel_status=True,
                    ).order_by(
                        '-rel_sqn'
                    ).values(
                        'id',
                        'rel_entry_date',
                        'rel_monthly_balance',
                        'rel_overall_balance',
                        'rel_sqn',
                    )[0]
                except Exception:
                    last_sqn = {
                        'id': None,
                        'rel_entry_date': data.rel_entry_date,
                        'rel_monthly_balance': 0,
                        'rel_overall_balance': 0,
                        'rel_sqn': 1,
                    }

                error = self._analytic_calculation(
                    date=last_sqn.get('rel_entry_date'),
                    sqn=last_sqn.get('rel_sqn'),
                    monthly_balance=last_sqn.get('rel_monthly_balance'),
                    overall_balance=last_sqn.get('rel_overall_balance'),
                    id=last_sqn.get('id')
                )
                if error:
                    self.request.session['error'] = error
                else:
                    self.request.session['success'] = 'Entry removed successfully.'  # noqa: E501
                return redirect('board:index')

    def _analytic_calculation(self, date, sqn, monthly_balance, overall_balance, id=None):  # noqa: E501
        # reorganization of each individual entry
        entries = Release.objects.filter(
            user=credentials(self.request.session['auth'], 'whoami'),
            rel_sqn__gte=sqn,
            rel_status=True,
        ).exclude(
            id=id
        ).order_by(
            'rel_sqn',
            'rel_entry_date',
        ).values(
            'id',
            'rel_entry_date',
            'subcategory__category__cat_type',
            'rel_amount'
        )

        last_monthly_balance = monthly_balance
        last_overall_balance = overall_balance
        last_entry_date = date
        last_sqn = sqn
        if id is None:
            last_sqn -= 1

        for each in entries:
            entry_amount = each['rel_amount'] * (1 if each['subcategory__category__cat_type'] == 1 else -1)  # noqa: E501
            if each['rel_entry_date'].strftime('%m') == last_entry_date.strftime('%m') and \
               each['rel_entry_date'].strftime('%Y') == last_entry_date.strftime('%Y'):  # noqa: E501
                last_monthly_balance = last_monthly_balance + entry_amount
            else:
                last_monthly_balance = entry_amount
            last_overall_balance = last_overall_balance + entry_amount
            last_sqn = last_sqn + 1
            last_entry_date = each['rel_entry_date']

            Release.objects.filter(
                id=each['id']
            ).update(
                rel_monthly_balance=last_monthly_balance,
                rel_overall_balance=last_overall_balance,
                rel_sqn=last_sqn,
                rel_date_updated=datetime.now()
            )

        # spreadsheet analytic calculator
        monthly_revenue = Release.objects.filter(
            user=credentials(self.request.session['auth'], 'whoami'),
            subcategory__category__cat_type=1,
            rel_status=True,
        ).extra(
            where=['MONTH(rel_entry_date)=%s and YEAR(rel_entry_date)=%s'],
            params=[date.strftime('%m'), date.strftime('%Y')]
        ).aggregate(total_revenue=Sum('rel_amount'))

        monthly_expenses = Release.objects.filter(
            user=credentials(self.request.session['auth'], 'whoami'),
            subcategory__category__cat_type=2,
            rel_status=True,
        ).extra(
            where=['MONTH(rel_entry_date)=%s and YEAR(rel_entry_date)=%s'],
            params=[date.strftime('%m'), date.strftime('%Y')]
        ).aggregate(total_expenses=Sum('rel_amount'))

        try:
            last_month_entry = Release.objects.filter(
                user=credentials(self.request.session['auth'], 'whoami'),
                rel_status=True,
            ).extra(
                where=['MONTH(rel_entry_date)=%s and YEAR(rel_entry_date)=%s'],
                params=[date.strftime('%m'), date.strftime('%Y')]
            ).order_by(
                '-rel_sqn'
            ).values(
                'rel_monthly_balance',
                'rel_overall_balance'
            )[0]
        except Exception:
            last_month_entry = {}

        json_data = {
            'monthly': {
                'revenue': str(monthly_revenue.get('total_revenue') or 0),
                'expenses': str(monthly_expenses.get('total_expenses') or 0),
                'balance': str(last_month_entry.get('rel_monthly_balance') or 0),  # noqa: E501
            },
            'overall': str(last_month_entry.get('rel_overall_balance') or 0)
        }

        try:
            current_analytic = Analytic.objects.filter(
                user=credentials(self.request.session['auth'], 'whoami'),
                ana_cycle=f'{date.strftime("%Y")}-{date.strftime("%m")}-01',
                ana_status=True
            )[0]

            current_analytic.ana_json = json.dumps(json_data)
            current_analytic.save()
        except Exception:
            request_form = {}
            request_form['user'] = credentials(self.request.session['auth'], 'whoami')  # noqa: E501
            request_form['ana_cycle'] = f'{date.strftime("%Y")}-{date.strftime("%m")}-01'  # noqa: E501
            request_form['ana_json'] = json.dumps(json_data)

            form = AnalyticForm(request_form)

            if form.is_valid():
                data = form.save(commit=False)
                data.ana_status = True
                data.save()
            else:
                return 'Unable to calculate balance report. Please send an ' \
                    'email to invo.finance2@gmail.com reporting the occurrence.'  # noqa: E501

        analytics = Analytic.objects.filter(
            user=credentials(self.request.session['auth'], 'whoami'),
            ana_cycle__gt=f'{date.strftime("%Y")}-{date.strftime("%m")}-01',
            ana_status=True
        ).all()

        if analytics:
            for each in analytics:
                monthly_revenue = Release.objects.filter(
                    user=credentials(self.request.session['auth'], 'whoami'),
                    subcategory__category__cat_type=1,
                    rel_status=True,
                ).extra(
                    where=['MONTH(rel_entry_date)=%s and YEAR(rel_entry_date)=%s'],  # noqa: E501
                    params=[each.ana_cycle.strftime('%m'), each.ana_cycle.strftime('%Y')]  # noqa: E501
                ).aggregate(total_revenue=Sum('rel_amount'))

                monthly_expenses = Release.objects.filter(
                    user=credentials(self.request.session['auth'], 'whoami'),
                    subcategory__category__cat_type=2,
                    rel_status=True,
                ).extra(
                    where=['MONTH(rel_entry_date)=%s and YEAR(rel_entry_date)=%s'],  # noqa: E501
                    params=[each.ana_cycle.strftime('%m'), each.ana_cycle.strftime('%Y')]  # noqa: E501
                ).aggregate(total_expenses=Sum('rel_amount'))

                try:
                    last_month_entry = Release.objects.filter(
                        user=credentials(self.request.session['auth'], 'whoami'),   # noqa: E501
                        rel_status=True,
                    ).extra(
                        where=['MONTH(rel_entry_date)=%s and YEAR(rel_entry_date)=%s'],  # noqa: E501
                        params=[each.ana_cycle.strftime('%m'), each.ana_cycle.strftime('%Y')]  # noqa: E501
                    ).order_by(
                        '-rel_sqn'
                    ).values(
                        'rel_monthly_balance',
                        'rel_overall_balance'
                    )[0]
                except Exception:
                    last_month_entry = {}
                    each.ana_status = False

                json_data = {
                    'monthly': {
                        'revenue': str(monthly_revenue.get('total_revenue') or 0),  # noqa: E501
                        'expenses': str(monthly_expenses.get('total_expenses') or 0),  # noqa: E501
                        'balance': str(last_month_entry.get('rel_monthly_balance') or 0),  # noqa: E501
                    },
                    'overall': str(last_month_entry.get('rel_overall_balance') or 0)  # noqa: E501
                }

                each.ana_json = json.dumps(json_data)
                each.save()

    def _balance_calculation(self, amount, date, subcategory, sqn):
        # spreadsheet balance calculator
        entry_type = SubCategory.objects.filter(
            category__cat_status=True,
            sub_status=True
        ).extra(
            where=['MD5(sub_slug)=%s'],
            params=[subcategory]
        ).values('category__cat_type')[0]
        amount = amount * (1 if entry_type['category__cat_type'] == 1 else -1)

        try:
            last_entry = Release.objects.filter(
                user=credentials(self.request.session['auth'], 'whoami'),
                rel_sqn__lt=sqn,
                rel_status=True,
            ).order_by(
                '-rel_sqn'
            ).values(
                'rel_sqn',
                'rel_entry_date',
                'rel_monthly_balance',
                'rel_overall_balance'
            )[0]

            if date.strftime('%m') == last_entry['rel_entry_date'].strftime('%m') and \
               date.strftime('%Y') == last_entry['rel_entry_date'].strftime('%Y'):  # noqa: E501
                entry_monthly_balance = last_entry['rel_monthly_balance'] + amount  # noqa: E501
            else:
                entry_monthly_balance = amount
            entry_overall_balance = last_entry['rel_overall_balance'] + amount
        except Exception:
            entry_monthly_balance = entry_overall_balance = amount
        return entry_monthly_balance, entry_overall_balance

    def _cleaning_number_string(self, number):
        # Also checking rel_amount because if the number comes with a comma
        # Django don't let me treat data before validation
        if number:
            return number.replace(',', '')

    def _error_exception(self, err):
        template = 'An exception of type {0} occurred. Arguments:\n{1!r}'
        print(template.format(type(err).__name__, err.args))
        return redirect('home:500')
