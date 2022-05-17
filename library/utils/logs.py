from home.forms.user_log_form import UserLogForm
from library.ipwhois.client import ipwhois
from library.utils.auth import credentials


def userlog(request, risk=0, comment=None):
    if request.META.get('REMOTE_ADDR') == '127.0.0.1':
        whois = {}
    else:
        whois = ipwhois(request.META.get('REMOTE_ADDR'))

    country_flag = _get_country_flag(whois.get('country_flag'))

    request_form = {
        'user': credentials(request.session.get('auth'), 'whoami'),
        'log_user_agent': request.META.get('HTTP_USER_AGENT'),
        'log_ip_address': request.META.get('REMOTE_ADDR'),
        'log_ip_type': whois.get('type'),
        'log_ip_country': whois.get('country'),
        'log_ip_country_flag': country_flag,
        'log_ip_region': whois.get('region'),
        'log_ip_city': whois.get('city'),
        'log_ip_latitude': whois.get('latitude'),
        'log_ip_longitude': whois.get('longitude'),
        'log_location': request.path,
        'log_method': request.META.get('REQUEST_METHOD'),
        'log_risk_level': risk,
        'log_risk_comment': comment
    }

    form = UserLogForm(request_form)
    if form.is_valid():
        form.save()


def _get_country_flag(country_flag):
    if country_flag:
        return country_flag.split('/')[::-1][0]
