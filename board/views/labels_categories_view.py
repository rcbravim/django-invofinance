import math
import os
from datetime import datetime

from board.forms.category_form import CategoryForm, SubCategoryForm
from board.models import Category, SubCategory
from django.shortcuts import redirect, render
from django.views import View
from library.utils.auth import credentials
from library.utils.decorators import auth_check
from library.utils.helper import paginator
from library.utils.logs import userlog
from library.utils.output_handle import general_valid_output
from slugify import slugify

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


class LabelsCategoriesView(View):
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
        categories_all = Category.objects.filter(
            user_id=credentials(self.request.session['auth'], 'whoami'),
            cat_status=True,
            subcategory__sub_status=True,
            subcategory__sub_name__icontains=self.request.GET.get('search', '')
        ).order_by(
            'cat_name',
            'subcategory__sub_name'
        ).values(
            'cat_name',
            'cat_slug',
            'cat_type',
            'cat_date_created',
            'subcategory__sub_name',
            'subcategory__sub_slug',
            'subcategory__sub_date_created'
        )

        # Appling type and label filters, if applicable
        if self.request.GET.get('type'):
            categories_all = categories_all.filter(
                cat_type=self.request.GET.get('type')
            )

        if self.request.GET.get('label'):
            categories_all = categories_all.extra(
                where=['MD5(cat_slug)=%s'],
                params=[self.request.GET.get('label')]
            )

        # Separate rows for exposure
        categories = categories_all[pg_offset:(pg_offset+PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(categories_all.count()/PG_LIMIT)

        # Select filter types
        labels = Category.objects.filter(
            user_id=credentials(self.request.session['auth'], 'whoami'),
            cat_status=True
        ).order_by(
            'cat_name'
        ).values(
            'cat_slug',
            'cat_name'
        )

        # Set page range
        pg_range = paginator(pg, total_pages)

        # set initial context
        context = {
            'labels': labels,
            'categories': categories,
            'filter': {
                'type': self.request.GET.get('type', ''),
                'search': self.request.GET.get('search', ''),
                'label': self.request.GET.get('label', '')
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
            template_name='board/pages/labels_categories.html',
            context=context
        )

    @auth_check
    def post(self, *args, **kwargs):
        match self.request.path:
            case '/board/labels/categories/edit/':
                # setting request form
                request_form = {}
                request_form['user'] = credentials(self.request.session['auth'], 'whoami')  # noqa: E501
                request_form['edit_category'] = self.request.POST.get('edit_category')  # noqa: E501

                # handling category name edit
                if self.request.POST.get('name') is not None:
                    request_form['cat_name'] = self.request.POST.get('name')
                    request_form['cat_type'] = self.request.POST.get('inlineRadio')  # noqa: E501

                    form = CategoryForm(request_form)

                    # check validation
                    if form.is_valid():
                        # finding category from subcategory slug
                        data = Category.objects.filter(
                            user_id=request_form.get('user'),
                            cat_status=True,
                            subcategory__sub_status=True,
                        ).extra(
                            where=['MD5(sub_slug)=%s'],
                            params=[request_form.get('edit_category')]
                        )[0]

                        # updating data and saving
                        data.cat_name = form.cleaned_data.get('cat_name')
                        data.cat_slug = slugify(
                            str(form.cleaned_data.get('cat_type')) +
                            credentials(self.request.session['auth'], 'login') +  # noqa: E501
                            form.cleaned_data.get('cat_name')
                        )
                        data.save()
                        request_form['category'] = data.id
                    else:
                        self.request.session['error'] = 'Invalid data, category name not edited:'  # noqa: E501
                        # handling error message to display
                        self.request.session['error'] += general_valid_output(
                            str(form.errors.get('cat_name'))
                        )
                        return redirect('board:labels_categories')
                else:
                    data = SubCategory.objects.filter(
                        sub_status=True
                    ).extra(
                        where=['MD5(sub_slug)=%s'],
                        params=[request_form.get('edit_category')]
                    ).values('category_id')[0]
                    request_form['category'] = data.get('category_id')

                request_form['sub_name'] = self.request.POST.get('subname')
                form = SubCategoryForm(request_form)

                if form.is_valid():
                    # get existing subcategory from database
                    data = SubCategory.objects.filter(
                        sub_status=True
                    ).extra(
                        where=['MD5(sub_slug)=%s'],
                        params=[form.data.get('edit_category')]
                    )[0]

                    # updating data and saving
                    data.sub_name = form.cleaned_data.get('sub_name')
                    data.sub_slug = slugify(
                        str(request_form.get('category')) +
                        credentials(self.request.session['auth'], 'login') +
                        data.sub_name
                    )
                    data.save()
                    if self.request.POST.get('name'):
                        self.request.session['success'] = 'Category and subcategory edited successfully.'  # noqa: E501
                    else:
                        self.request.session['success'] = 'Subcategory edited successfully.'  # noqa: E501
                else:
                    if self.request.POST.get('name'):
                        self.request.session['success'] = 'Category edited successfully.'  # noqa: E501
                    else:
                        self.request.session['error'] = 'Invalid data, subcategory not edited:'  # noqa: E501
                        # handling error message to display
                        self.request.session['error'] += general_valid_output(
                            str(form.errors.get('sub_name'))
                        )
                return redirect('board:labels_categories')

            case '/board/labels/categories/delete/':
                # get existing beneficiary from database
                data = SubCategory.objects.filter(
                    sub_status=True
                ).extra(
                    where=['MD5(sub_slug)=%s'],
                    params=[self.request.POST.get('del_subcategory')]
                )[0]

                # updating data and saving - for delete status = 0
                data.sub_slug = slugify(
                    datetime.now().strftime('%m/%d/%Y, %H:%M:%S') +
                    data.sub_slug
                )
                data.sub_status = False
                data.sub_date_deleted = datetime.now()
                data.save()

                self.request.session['success'] = 'Subcategory removed successfully.'  # noqa: E501
                return redirect('board:labels_categories')
