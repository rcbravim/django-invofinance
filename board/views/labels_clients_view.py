import math
import os
from datetime import datetime

from board.forms.client_form import ClientForm
from board.models import Client, Country
from django.shortcuts import redirect, render
from django.views import View
from library.utils.auth import credentials
from library.utils.decorators import auth_check
from library.utils.helper import paginator
from library.utils.logs import userlog
from library.utils.output_handle import general_valid_output
from slugify import slugify

PG_LIMIT = int(os.environ.get('PG_LIMIT', 25))


class LabelsClientsView(View):
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
        clients_all = Client.objects.select_related(
            'country',
            'state'
        ).filter(
            user=credentials(self.request.session['auth'], 'whoami'),
            cli_name__icontains=self.request.GET.get('search', ''),
            cli_status=True,
            country__cou_status=True,
            state__sta_status=True
        ).order_by(
            'country__cou_name',
            'state__sta_name',
            'cli_name',
        ).values(
            'cli_name',
            'cli_slug',
            'cli_date_created',
            'country__cou_name',
            'country__cou_image',
            'state__sta_name',
        )

        # Appling country filters, if applicable
        if self.request.GET.get('country'):
            clients_all = clients_all.extra(
                where=['MD5(board_client.country_id)=%s'],
                params=[self.request.GET.get('country')]
            )

        # Separate rows for exposure
        clients = clients_all[pg_offset:(pg_offset+PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(clients_all.count()/PG_LIMIT)

        # Select filter types
        countries = Country.objects.filter(
            cou_status=True,
            client__cli_status=True
        ).order_by(
            'cou_name'
        ).values(
            'id',
            'cou_name'
        ).distinct()

        # Set page range
        pg_range = paginator(pg, total_pages)

        # set initial context
        context = {
            'countries': countries,
            'clients': clients,
            'filter': {
                'country': self.request.GET.get('country', ''),
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
            template_name='board/pages/labels_clients.html',
            context=context
        )

    @auth_check
    def post(self, *args, **kwargs):
        match self.request.path:
            case '/board/labels/clients/edit/':
                # setting request form
                request_form = {}
                request_form['user'] = credentials(self.request.session['auth'], 'whoami')  # noqa: E501
                request_form['cli_name'] = self.request.POST.get('client')
                request_form['state'] = self.request.POST.get('state')
                request_form['cli_city'] = self.request.POST.get('city')
                request_form['cli_email'] = self.request.POST.get('email')
                request_form['cli_phone'] = self.request.POST.get('phone')
                request_form['cli_responsible'] = self.request.POST.get('responsible')  # noqa: E501
                request_form['edit_client'] = self.request.POST.get('edit_client')  # noqa: E501

                country = Country.objects.filter(
                    cou_status=True
                ).extra(
                    where=['MD5(id)=%s'],
                    params=[self.request.POST.get('country')]
                ).values('id')[0]

                request_form['country'] = country.get('id')

                form = ClientForm(request_form)

                if form.is_valid():
                    # get existing subcategory from database
                    data = Client.objects.filter(
                        cli_status=True
                    ).extra(
                        where=['MD5(cli_slug)=%s'],
                        params=[form.data.get('edit_client')]
                    )[0]

                    # updating data and saving
                    data.cli_name = form.cleaned_data.get('cli_name')
                    data.cli_slug = slugify(
                        str(request_form.get('country')) +
                        str(request_form.get('state')) +
                        credentials(self.request.session['auth'], 'login') +
                        data.cli_name
                    )
                    data.state_id = form.cleaned_data.get('state').id
                    data.country_id = form.cleaned_data.get('country').id
                    data.cli_city = form.cleaned_data.get('cli_city')
                    data.cli_email = form.cleaned_data.get('cli_email')
                    data.cli_phone = form.cleaned_data.get('cli_phone')
                    data.cli_responsible = form.cleaned_data.get('cli_responsible')  # noqa: E501
                    data.save()
                    self.request.session['success'] = 'Client edited successfully.'  # noqa: E501
                else:
                    self.request.session['error'] = 'Invalid data, client not edited:'  # noqa: E501
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
                return redirect('board:labels_clients')

            case '/board/labels/clients/delete/':
                # get existing client from database
                data = Client.objects.filter(
                    cli_status=True
                ).extra(
                    where=['MD5(cli_slug)=%s'],
                    params=[self.request.POST.get('del_client')]
                )[0]

                # updating data and saving - for delete status = 0
                data.cli_slug = slugify(
                    datetime.now().strftime('%m/%d/%Y, %H:%M:%S') +
                    data.cli_slug
                )
                data.cli_status = False
                data.cli_date_deleted = datetime.now()
                data.save()

                self.request.session['success'] = 'Client removed successfully.'  # noqa: E501
                return redirect('board:labels_clients')
