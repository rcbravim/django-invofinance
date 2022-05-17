import os

import jwt


def auth(payload):
    return jwt.encode(
        payload=payload,
        key=os.environ.get('JWT_SECRET', 'INSECURE'),
        algorithm=os.environ.get('JWT_ALGORITHM', 'INSECURE')
    )


def credentials(payload, key):
    if payload:
        decoded = jwt.decode(
            jwt=payload,
            key=os.environ.get('JWT_SECRET', 'INSECURE'),
            algorithms=[os.environ.get('JWT_ALGORITHM', 'INSECURE')]
        )
        return decoded[key]
