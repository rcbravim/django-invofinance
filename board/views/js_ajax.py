import json

from board.models import (Beneficiary, Category, Client, Financial, Release,
                          State, SubCategory)
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F, Func
from django.http import HttpResponse
from django.views import View
from library.utils.auth import credentials
from library.utils.decorators import auth_check
from library.utils.helper import hash_gen
from library.utils.logs import userlog


class JsView(View):
    @auth_check
    def dispatch(self, *args, **kwargs):
        userlog(self.request)
        return super().dispatch(self.request, *args, **kwargs)

    @auth_check
    def post(self, *args, **kwargs):
        if _is_ajax(self.request) and self.request.POST:
            match self.request.path:
                case '/board/js/':
                    detail = Release.objects.select_related(
                        'subcategory',
                        'beneficiary',
                        'client',
                        'financial_cost_center',
                        'financial_account',
                    ).filter(
                        user=credentials(
                            self.request.session['auth'], 'whoami'
                        ),
                        rel_status=True
                    ).extra(
                        where=['MD5(rel_slug)=%s'],
                        params=[self.request.POST.get('detail')]
                    ).values(
                        'rel_entry_date',
                        'rel_gen_status',
                        'rel_amount',
                        'rel_description',
                        'subcategory__category',
                        'subcategory__sub_name',
                        'subcategory__sub_slug',
                        'subcategory__category__cat_name',
                        'subcategory__category__cat_type',
                        'subcategory__category__cat_slug',
                        'beneficiary__ben_name',
                        'beneficiary__ben_slug',
                        'beneficiary__beneficiary_category__cat_description',
                        'client__cli_name',
                        'client__cli_slug',
                        'client__cli_city',
                        'client__cli_email',
                        'client__cli_phone',
                        'client__cli_responsible',
                        'client__country__cou_name',
                        'client__country__cou_image',
                        'client__state__sta_name',
                        'financial_cost_center__fin_slug',
                        'financial_cost_center__fin_cost_center',
                        'financial_cost_center__fin_description',
                        'financial_account__fin_slug',
                        'financial_account__fin_bank_name',
                        'financial_account__fin_bank_branch',
                        'financial_account__fin_bank_account',
                    )[0]

                    subcategories = SubCategory.objects.filter(
                        category=detail.get('subcategory__category'),
                        sub_status=True,
                    ).order_by(
                        'sub_name'
                    ).values(
                        name=F('sub_name'),
                        slug=Func(F('sub_slug'), function='MD5')
                    )

                    data = {
                        'entry': {
                            'date': detail.get('rel_entry_date'),
                            'status': detail.get('rel_gen_status'),
                            'amount': detail.get('rel_amount'),
                            'description': detail.get('rel_description'),
                        },
                        'subcategory': {
                            'name': detail.get('subcategory__sub_name'),
                            'value': hash_gen(detail.get('subcategory__sub_slug')),  # noqa: E501
                            'list': list(subcategories),
                            'category_name': detail.get('subcategory__category__cat_name'),  # noqa: E501
                            'category_type': detail.get('subcategory__category__cat_type'),  # noqa: E501
                            'category_value': hash_gen(str(detail.get('subcategory__category__cat_slug'))),  # noqa: E501
                        },
                        'beneficiary': {
                            'name': detail.get('beneficiary__ben_name'),
                            'value': hash_gen(detail.get('beneficiary__ben_slug')),  # noqa: E501
                            'category': detail.get('beneficiary__beneficiary_category__cat_description'),  # noqa: E501
                        },
                        'financial_account': {
                            'bank': detail.get('financial_account__fin_bank_name'),  # noqa: E501
                            'branch': detail.get('financial_account__fin_bank_branch'),  # noqa: E501
                            'account': detail.get('financial_account__fin_bank_account'),  # noqa: E501
                            'value': hash_gen(detail.get('financial_account__fin_slug')),  # noqa: E501
                        },
                        'client': {},
                        'financial_cost_center': {}
                    }

                    if detail.get('client__cli_name'):
                        data['client']['name'] = detail.get('client__cli_name')
                        data['client']['value'] = hash_gen(detail.get('client__cli_slug'))  # noqa: E501
                        data['client']['city'] = detail.get('client__cli_city')
                        data['client']['email'] = detail.get('client__cli_email')  # noqa: E501
                        data['client']['phone'] = detail.get('client__cli_phone')  # noqa: E501
                        data['client']['responsible'] = detail.get('client__cli_responsible')  # noqa: E501
                        data['client']['region'] = detail.get('client__country__cou_name')  # noqa: E501
                        data['client']['flag'] = detail.get('client__country__cou_image')  # noqa: E501
                        data['client']['state'] = detail.get('client__state__sta_name')  # noqa: E501

                    if detail.get('financial_cost_center__fin_cost_center'):
                        data['financial_cost_center']['name'] = detail.get('financial_cost_center__fin_cost_center')  # noqa: E501
                        data['financial_cost_center']['description'] = detail.get('financial_cost_center__fin_description')  # noqa: E501
                        data['financial_cost_center']['value'] = hash_gen(detail.get('financial_cost_center__fin_slug'))  # noqa: E501

                    return HttpResponse(
                        json.dumps(data, cls=DjangoJSONEncoder)
                    )
                case '/board/category/js/':
                    data = SubCategory.objects.select_related(
                        'category'
                    ).filter(
                        sub_status=True,
                        category__cat_status=True,
                    ).extra(
                        where=['MD5(cat_slug)=%s'],
                        params=[self.request.POST.get('category')]
                    ).order_by(
                        'sub_name'
                    ).values(
                        subcategory=F('sub_name'),
                        slug=Func(F('sub_slug'), function='MD5')
                    )

                    return HttpResponse(
                        json.dumps(list(data), cls=DjangoJSONEncoder)
                    )
                case '/board/labels/beneficiaries/js/':
                    detail = Beneficiary.objects.select_related(
                        'beneficiary_category'
                    ).filter(
                        ben_status=True,
                    ).extra(
                        where=['MD5(ben_slug)=%s'],
                        params=[self.request.POST.get('detail')]
                    ).values(
                        'ben_name',
                        'ben_date_created',
                        'beneficiary_category__cat_description'
                    )[0]

                    data = {
                        'register_date': detail.get('ben_date_created'),
                        'name': detail.get('ben_name'),
                        'description': detail.get('beneficiary_category__cat_description')  # noqa: E501
                    }

                    return HttpResponse(
                        json.dumps(data, cls=DjangoJSONEncoder)
                    )
                case '/board/labels/categories/js/':
                    detail = SubCategory.objects.select_related(
                        'category'
                    ).filter(
                        sub_status=True,
                        category__cat_status=True,
                    ).extra(
                        where=['MD5(sub_slug)=%s'],
                        params=[self.request.POST.get('detail')]
                    ).values(
                        'sub_name',
                        'sub_date_created',
                        'category__cat_name',
                        'category__cat_type'
                    )[0]

                    data = {
                        'register_date': detail.get('sub_date_created'),
                        'subcategory': detail.get('sub_name'),
                        'category': detail.get('category__cat_name'),
                        'type': detail.get('category__cat_type')
                    }

                    return HttpResponse(
                        json.dumps(data, cls=DjangoJSONEncoder)
                    )
                case '/board/labels/categories/form/js/':
                    name = Category.objects.filter(
                        user=credentials(
                            self.request.session['auth'],
                            'whoami'
                        ),
                        cat_status=True,
                    ).extra(
                        where=['MD5(cat_slug)=%s'],
                        params=[self.request.POST.get('name')]
                    ).values('cat_type')

                    if name:
                        data = {'type': name[0].get('cat_type')}
                    else:
                        data = False

                    return HttpResponse(
                        json.dumps(data, cls=DjangoJSONEncoder)
                    )
                case '/board/labels/clients/js/':
                    client = Client.objects.select_related(
                        'country',
                        'state'
                    ).filter(
                        cli_status=True,
                        country__cou_status=True,
                        state__sta_status=True,
                    ).extra(
                        where=['MD5(cli_slug)=%s'],
                        params=[self.request.POST.get('detail')]
                    ).values(
                        'cli_name',
                        'cli_city',
                        'cli_email',
                        'cli_phone',
                        'cli_responsible',
                        'cli_date_created',
                        'country__id',
                        'country__cou_name',
                        'country__cou_image',
                        'state__id',
                        'state__sta_name'
                    )[0]

                    states = State.objects.select_related(
                        'country'
                    ).filter(
                        country=client.get('country__id'),
                        sta_status=True,
                        country__cou_status=True,
                    ).order_by(
                        'sta_name'
                    ).values(
                        'id',
                        state=F('sta_name'),
                        region=F('country__cou_name')
                    )

                    data = {
                        'register_date': client.get('cli_date_created'),
                        'client': client.get('cli_name'),
                        'city': client.get('cli_city'),
                        'email': client.get('cli_email'),
                        'phone': client.get('cli_phone'),
                        'responsible': client.get('cli_responsible'),
                        'region': client.get('country__cou_name'),
                        'region_val': hash_gen(str(client.get('country__id'))),
                        'flag': client.get('country__cou_image'),
                        'state': client.get('state__sta_name'),
                        'state_list': list(states),
                        'state_val': client.get('state__id')
                    }

                    return HttpResponse(
                        json.dumps(data, cls=DjangoJSONEncoder)
                    )
                case '/board/labels/clients/form/js/':
                    data = State.objects.select_related(
                        'country'
                    ).filter(
                        sta_status=True,
                        country__cou_status=True,
                    ).extra(
                        where=['MD5(country_id)=%s'],
                        params=[self.request.POST.get('country')]
                    ).order_by(
                        'sta_name'
                    ).values(
                        'id',
                        state=F('sta_name'),
                        region=F('country__cou_name')
                    )

                    return HttpResponse(
                        json.dumps(list(data), cls=DjangoJSONEncoder)
                    )
                case '/board/labels/financial/js/':
                    detail = Financial.objects.filter(
                        fin_status=True,
                    ).extra(
                        where=['MD5(fin_slug)=%s'],
                        params=[self.request.POST.get('detail')]
                    ).values(
                        'fin_cost_center',
                        'fin_description',
                        'fin_bank_name',
                        'fin_bank_branch',
                        'fin_bank_account',
                        'fin_type',
                        'fin_date_created',
                    )[0]

                    data = {
                        'register_date': detail.get('fin_date_created'),
                        'cost_center': detail.get('fin_cost_center'),
                        'description': detail.get('fin_description'),
                        'bank': detail.get('fin_bank_name'),
                        'branch': detail.get('fin_bank_branch'),
                        'account': detail.get('fin_bank_account'),
                        'type': detail.get('fin_type'),
                    }

                    return HttpResponse(
                        json.dumps(data, cls=DjangoJSONEncoder)
                    )


def _is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
