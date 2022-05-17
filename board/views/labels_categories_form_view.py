from datetime import datetime

from board.forms.category_form import CategoryForm, SubCategoryForm
from board.models import Category, SubCategory
from django.shortcuts import redirect, render
from django.views import View
from library.utils.auth import credentials
from library.utils.decorators import auth_check
from library.utils.logs import userlog
from library.utils.output_handle import general_valid_output
from slugify import slugify


class LabelsCategoriesFormView(View):
    @auth_check
    def dispatch(self, *args, **kwargs):
        userlog(self.request)
        return super().dispatch(self.request, *args, **kwargs)

    @auth_check
    def get(self, *args, **kwargs):
        categories = Category.objects.filter(
            user_id=credentials(self.request.session['auth'], 'whoami'),
            cat_status=True
        ).order_by(
            'cat_name'
        ).values(
            'cat_name',
            'cat_slug'
        )

        # set initial context
        context = {
            'categories': categories
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
            template_name='board/pages/labels_categories_form.html',
            context=context
        )

    @auth_check
    def post(self, *args, **kwargs):
        match self.request.path:
            case '/board/labels/categories/form/new/':
                # update request to treat data and add user
                request_form = {}
                request_form['cat_name'] = self.request.POST.get('outer-group[0][name]')  # noqa: E501
                request_form['cat_type'] = self.request.POST.get('outer-group[0][inlineRadioOptions]')  # noqa: E501
                request_form['user'] = credentials(self.request.session['auth'], 'whoami')  # noqa: E501

                if request_form.get('cat_type'):
                    form = CategoryForm(request_form)

                    if form.is_valid():
                        data = form.save(commit=False)

                        # adding remaining data and saving
                        data.cat_slug = slugify(
                            str(data.cat_type) +
                            credentials(
                                self.request.session['auth'], 'login'
                            ) +
                            data.cat_name
                        )
                        data.cat_status = True
                        data.save()
                        request_form['category'] = data.id
                        new = True
                        self.request.session['success'] = 'Category added successfully.'  # noqa: E501
                    else:
                        self.request.session['error'] = 'Invalid data, category not registered:'  # noqa: E501
                        # handling error message to display
                        self.request.session['error'] += general_valid_output(
                            str(form.errors.get('cat_name'))
                        )
                        return redirect('board:labels_categories_form')
                else:
                    data = Category.objects.filter(
                        user=request_form.get('user'),
                        cat_status=True
                    ).extra(
                        where=['MD5(cat_slug)=%s'],
                        params=[request_form.get('cat_name')]
                    ).values('id')[0]

                    request_form['category'] = data.get('id')
                    new = False

                key_list = [key for key in self.request.POST if 'subname' in key]  # noqa: E501

                if key_list:
                    for i in key_list:
                        request_form['sub_name'] = self.request.POST.get(i)

                        form = SubCategoryForm(request_form)
                        if form.is_valid():
                            data = form.save(commit=False)

                            # adding remaining data and saving
                            data.sub_slug = slugify(
                                str(request_form.get('category')) +
                                credentials(
                                    self.request.session['auth'], 'login'
                                ) +
                                data.sub_name
                            )
                            data.sub_status = True
                            data.save()
                            if new:
                                self.request.session['success'] = 'Category and subcategory(ies) added successfully.'  # noqa: E501
                            else:
                                self.request.session['success'] = 'Subcategory(ies) added successfully.'  # noqa: E501
                        else:
                            self.request.session['error'] = 'Invalid data, subcategory not registered:'  # noqa: E501
                            # handling error message to display
                            self.request.session['error'] += general_valid_output(  # noqa: E501
                                str(form.errors.get('sub_name'))
                            )
                elif not new:
                    self.request.session['error'] = 'Invalid data! You must ' \
                        'add at least one subcategory when using an existing category.'  # noqa: E501

                return redirect('board:labels_categories_form')

            case '/board/labels/categories/form/delete/category/':
                # get existing beneficiary type from database
                data = Category.objects.filter(
                    user=credentials(self.request.session['auth'], 'whoami'),
                    cat_status=True
                ).extra(
                    where=['MD5(cat_slug)=%s'],
                    params=[self.request.POST.get('name')]
                )[0]

                # updating all subcategories attached to this category
                # and saving - for delete status = 0
                queryset = SubCategory.objects.filter(
                    category=data.id,
                    sub_status=True
                )

                for item in queryset:
                    item.sub_slug = slugify(
                        datetime.now().strftime('%m/%d/%Y, %H:%M:%S') +
                        item.sub_slug
                    )
                    item.sub_status = False
                    item.sub_date_deleted = datetime.now()
                    item.save()

                # updating type data and saving - for delete status = 0
                data.cat_slug = slugify(
                    datetime.now().strftime('%m/%d/%Y, %H:%M:%S') +
                    data.cat_slug
                )
                data.cat_status = False
                data.cat_date_deleted = datetime.now()
                data.save()

                self.request.session['success'] = 'Category removed successfully.'  # noqa: E501
                return redirect('board:labels_categories_form')
