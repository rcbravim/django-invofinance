import os
from datetime import datetime, timedelta

import jwt
from django.shortcuts import redirect
from library.utils.auth import auth


def auth_check(func) -> dict:
    def wrapped(self, *args, **kwargs):
        func_list = ['IndexView.get', 'IndexView.post', 'RegisterView.get',
                     'RegisterView.post']
        if func.__qualname__ not in func_list:
            if 'auth' not in self.request.session:
                self.request.session['error'] = 'You are not authenticated.'
                return redirect('home:index')
            else:
                try:
                    # check if credentials are up to date
                    payload = jwt.decode(
                        jwt=self.request.session['auth'],
                        key=os.environ.get('JWT_SECRET', 'INSECURE'),
                        algorithms=[os.environ.get('JWT_ALGORITHM', 'INSECURE')]  # noqa: E501
                    )

                    # renew credentials
                    payload['exp'] = (datetime.now() + timedelta(minutes=30)).strftime('%s')  # noqa: E501
                    self.request.session['auth'] = auth(payload=payload)

                    return func(self)
                except jwt.ExpiredSignatureError:
                    del self.request.session['auth']
                    self.request.session['error'] = 'Your session has expired, please login.'  # noqa: E501
                    return redirect('home:index')
                except jwt.InvalidTokenError:
                    del self.request.session['auth']
                    self.request.session['error'] = 'Invalid token.'
                    return redirect('home:index')
                except Exception as err:
                    print(err)
                    """ del self.request.session['auth']
                    return redirect('home:500') """
        else:
            if 'auth' in self.request.session:
                del self.request.session['auth']
            return func(self)
    return wrapped  # type: ignore
