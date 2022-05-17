import math
import os
from datetime import datetime

from board.forms.beneficiary_category_form import (BeneficiaryCategoryForm,
                                                   BeneficiaryForm)
from board.models import Beneficiary, BeneficiaryCategory
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View
from library.utils.auth import credentials
from library.utils.decorators import auth_check
from library.utils.helper import paginator
from library.utils.logs import userlog
from library.utils.output_handle import general_valid_output
from slugify import slugify

PG_LIMIT = int(os.environ.get('PG_LIMIT', 25))


class LabelsBeneficiariesView(View):
    @auth_check
    def dispatch(self, *args, **kwargs):
        userlog(self.request)
        return super().dispatch(self.request, *args, **kwargs)

    @auth_check
    def get(self, *args, **kwargs):
        # Set offset and limit
        pg = int(self.request.GET.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT

        # Select all rows
        beneficiaries_all = Beneficiary.objects.select_related(
            'beneficiary_category'
        ).filter(
            user_id=credentials(self.request.session['auth'], 'whoami'),
            ben_name__icontains=self.request.GET.get('search', ''),
            ben_status=True
        ).order_by(
            'beneficiary_category__cat_description',
            'ben_name'
        ).values(
            'ben_slug',
            'ben_name',
            'ben_date_created',
            'beneficiary_category__cat_description',
            'beneficiary_category__cat_slug'
        )

        # Appling type filter, if applicable
        if self.request.GET.get('type'):
            beneficiaries_all = beneficiaries_all.extra(
                where=['MD5(cat_slug)=%s'],
                params=[self.request.GET.get('type')]
            )

        # Separate rows for exposure
        beneficiaries = beneficiaries_all[pg_offset:(pg_offset+PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(beneficiaries_all.count()/PG_LIMIT)

        # Select filter types
        types = BeneficiaryCategory.objects.filter(
            Q(
                Q(user_id=credentials(self.request.session['auth'], 'whoami')) |  # noqa: E501
                Q(user_id__isnull=True)
            ),
            cat_status=True
        ).order_by(
            'cat_description'
        ).values(
            'cat_slug',
            'cat_description'
        )

        # Set page range
        pg_range = paginator(pg, total_pages)

        # set initial context
        context = {
            'types': types,
            'beneficiaries': beneficiaries,
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
            template_name='board/pages/labels_beneficiaries.html',
            context=context
        )

    @auth_check
    def post(self, *args, **kwargs):
        match self.request.path:
            case '/board/labels/beneficiaries/edit/':
                # setting request form
                request_form = {}
                request_form['user'] = credentials(self.request.session['auth'], 'whoami')  # noqa: E501
                request_form['edit_beneficiary'] = self.request.POST.get('edit_beneficiary')  # noqa: E501

                # handling beneficiary type edit
                if self.request.POST.get('description') is not None:
                    request_form['cat_description'] = self.request.POST.get('description')  # noqa: E501

                    form = BeneficiaryCategoryForm(request_form)

                    # check validation
                    if form.is_valid():
                        # get existing description from database
                        data = BeneficiaryCategory.objects.filter(
                            id=form.data.get('beneficiary_type'),
                            cat_status=True
                        )[0]

                        # updating data and saving
                        data.cat_description = form.cleaned_data.get('cat_description')  # noqa: E501
                        data.cat_slug = slugify(
                            credentials(self.request.session['auth'], 'login') +  # noqa: E501
                            form.cleaned_data.get('cat_description')
                        )
                        data.save()
                        request_form['beneficiary_category'] = data.id
                    else:
                        self.request.session['error'] = 'Invalid data, beneficiary type not edited:'  # noqa: E501
                        # handling error message to display
                        self.request.session['error'] += general_valid_output(
                            str(form.errors.get('cat_description'))
                        )
                        return redirect('board:labels_beneficiaries')
                else:
                    data = Beneficiary.objects.filter(
                        user=request_form.get('user'),
                        ben_status=True
                    ).extra(
                        where=['MD5(ben_slug)=%s'],
                        params=[request_form.get('edit_beneficiary')]
                    ).values('beneficiary_category_id')[0]
                    request_form['beneficiary_category'] = data.get('beneficiary_category_id')  # noqa: E501

                request_form['ben_name'] = self.request.POST.get('name')
                form = BeneficiaryForm(request_form)
                if form.is_valid():

                    # get existing beneficiary from database
                    data = Beneficiary.objects.filter(
                        ben_status=True
                    ).extra(
                        where=['MD5(ben_slug)=%s'],
                        params=[form.data.get('edit_beneficiary')]
                    )[0]

                    # updating data and saving
                    data.ben_name = form.cleaned_data.get('ben_name')
                    data.ben_slug = slugify(
                        str(data.beneficiary_category_id) +
                        credentials(self.request.session['auth'], 'login') +
                        data.ben_name
                    )
                    data.save()
                    if self.request.POST.get('description'):
                        self.request.session['success'] = 'Beneficiary type and name edited successfully.'  # noqa: E501
                    else:
                        self.request.session['success'] = 'Beneficiary name edited successfully.'  # noqa: E501
                else:
                    if self.request.POST.get('description'):
                        self.request.session['success'] = 'Beneficiary type edited successfully.'  # noqa: E501
                    else:
                        self.request.session['error'] = 'Invalid data, beneficiary not edited:'  # noqa: E501
                        # handling error message to display
                        self.request.session['error'] += general_valid_output(
                            str(form.errors.get('ben_name'))
                        )
                return redirect('board:labels_beneficiaries')

            case '/board/labels/beneficiaries/delete/':
                # get existing beneficiary from database
                data = Beneficiary.objects.filter(
                    ben_status=True
                ).extra(
                    where=['MD5(ben_slug)=%s'],
                    params=[self.request.POST.get('del_beneficiary')]
                )[0]

                # updating data and saving - for delete status = 0
                data.ben_slug = slugify(
                    datetime.now().strftime('%m/%d/%Y, %H:%M:%S') +
                    data.ben_slug
                )
                data.ben_status = False
                data.ben_date_deleted = datetime.now()
                data.save()

                self.request.session['success'] = 'Beneficiary name removed successfully.'  # noqa: E501
                return redirect('board:labels_beneficiaries')
