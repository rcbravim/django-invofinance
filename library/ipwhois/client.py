import requests


def ipwhois(ip_address):
    curlopt_url = 'http://ipwhois.app/json/' + ip_address

    response = requests.request(
        method='GET',
        url=curlopt_url,
        data={},
        timeout=12000
    )
    return response.json()
