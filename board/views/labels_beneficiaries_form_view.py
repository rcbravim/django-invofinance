from datetime import datetime

from board.forms.beneficiary_category_form import (BeneficiaryCategoryForm,
                                                   BeneficiaryForm)
from board.models import Beneficiary, BeneficiaryCategory
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View
from library.utils.auth import credentials
from library.utils.decorators import auth_check
from library.utils.logs import userlog
from library.utils.output_handle import general_valid_output
from slugify import slugify


class LabelsBeneficiariesFormView(View):
    @auth_check
    def dispatch(self, *args, **kwargs):
        userlog(self.request)
        return super().dispatch(self.request, *args, **kwargs)

    @auth_check
    def get(self, *args, **kwargs):
        # dropdown menu type
        types = BeneficiaryCategory.objects.filter(
            Q(
                Q(user_id=credentials(self.request.session['auth'], 'whoami')) |  # noqa: E501
                Q(user_id__isnull=True)
            ),
            cat_status=True
        ).order_by(
            'cat_description'
        ).values(
            'user_id',
            'cat_description',
            'cat_slug'
        )

        # set initial context
        context = {
            'types': types
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
            template_name='board/pages/labels_beneficiaries_form.html',
            context=context
        )

    @auth_check
    def post(self, *args, **kwargs):
        match self.request.path:
            case '/board/labels/beneficiaries/form/new/':
                # update request to add user
                request_form = {}
                request_form['cat_description'] = self.request.POST.get('description')  # noqa: E501
                request_form['user'] = credentials(self.request.session['auth'], 'whoami')  # noqa: E501

                form = BeneficiaryCategoryForm(request_form)

                # check validation
                if form.is_valid():
                    try:
                        data = BeneficiaryCategory.objects.filter(
                            Q(
                                Q(user=request_form.get('user')) |
                                Q(user__isnull=True)
                            ),
                            cat_status=True
                        ).extra(
                            where=['MD5(cat_slug)=%s'],
                            params=[request_form.get('cat_description')]
                        ).values('id')[0]
                        new = False
                        request_form['beneficiary_category'] = data.get('id')
                    except Exception:
                        data = form.save(commit=False)

                        # adding remaining data and saving
                        data.cat_slug = slugify(
                            credentials(
                                self.request.session['auth'], 'login'
                            ) +
                            data.cat_description
                        )
                        data.cat_status = True
                        data.save()

                        new = True
                        request_form['beneficiary_category'] = data.id

                    request_form['ben_name'] = self.request.POST.get('name')
                    request_form['user'] = credentials(self.request.session['auth'], 'whoami')  # noqa: E501

                    form = BeneficiaryForm(request_form)
                    if form.is_valid():
                        data = form.save(commit=False)

                        # adding remaining data and saving
                        data.beneficiary_category_id = request_form.get('beneficiary_category')  # noqa: E501
                        data.ben_slug = slugify(
                            str(request_form.get('beneficiary_category')) +
                            credentials(
                                self.request.session['auth'], 'login'
                            ) +
                            data.ben_name
                        )
                        data.ben_status = True
                        data.save()
                        if new:
                            self.request.session['success'] = 'Beneficiary type and name added successfully.'  # noqa: E501
                        else:
                            self.request.session['success'] = 'Beneficiary name added successfully.'  # noqa: E501
                    else:
                        self.request.session['error'] = 'Invalid data, beneficiary name not registered:'  # noqa: E501
                        # handling error message to display
                        self.request.session['error'] += general_valid_output(
                            str(form.errors.get('ben_name'))
                        )
                else:
                    self.request.session['error'] = 'Invalid data, beneficiary type not registered:'  # noqa: E501
                    # handling error message to display
                    self.request.session['error'] += general_valid_output(
                        str(form.errors.get('cat_description'))
                    )
                return redirect('board:labels_beneficiaries_form')

            case '/board/labels/beneficiaries/form/delete/type/':
                # get existing beneficiary type from database
                data = BeneficiaryCategory.objects.filter(
                    user=credentials(self.request.session['auth'], 'whoami'),
                    cat_status=True
                ).extra(
                    where=['MD5(cat_slug)=%s'],
                    params=[self.request.POST.get('description')]
                )[0]

                # updating all beneficiaries attached to this type
                # and saving - for delete status = 0
                queryset = Beneficiary.objects.filter(
                    beneficiary_category=data.id,
                    ben_status=True
                )

                for item in queryset:
                    item.ben_slug = slugify(
                        datetime.now().strftime('%m/%d/%Y, %H:%M:%S') +
                        item.ben_slug
                    )
                    item.ben_status = False
                    item.ben_date_deleted = datetime.now()
                    item.save()

                # updating type data and saving - for delete status = 0
                data.cat_slug = slugify(
                    datetime.now().strftime('%m/%d/%Y, %H:%M:%S') +
                    data.cat_slug
                )
                data.cat_status = False
                data.cat_date_deleted = datetime.now()
                data.save()

                self.request.session['success'] = 'Beneficiary type removed successfully.'  # noqa: E501
                return redirect('board:labels_beneficiaries_form')
