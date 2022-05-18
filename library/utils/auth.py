import os

import jwt


def auth(payload):
    return jwt.encode(
        payload=payload,
        key=os.getenv('JWT_SECRET', 'INSECURE'),
        algorithm=os.getenv('JWT_ALGORITHM', 'INSECURE')
    )


def credentials(payload, key):
    if payload:
        decoded = jwt.decode(
            jwt=payload,
            key=os.getenv('JWT_SECRET', 'INSECURE'),
            algorithms=[os.getenv('JWT_ALGORITHM', 'INSECURE')],
            options={'verify_signature': False}
        )
        return decoded[key]
