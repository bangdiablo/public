import random, string

from datetime import datetime
from ..utils.AESCipher import AESCipher


def login(user, meta, language):

    if user:
        payload = {
            'userId': user.bu_id,
            'email': user.bu_email,
            'iat': datetime.now().timestamp(),
        }

        authKey = ""

        for i in range(16):
            authKey += random.choice(string.ascii_letters)

        cipher = AESCipher(authKey)
        accessToken = cipher.encrypt(str(payload))
        accessToken = accessToken.decode('utf-8')

        print("accessToken: " + accessToken)
        # user.auth_token = accessToken
        # user.last_signin_ip = meta.get('REMOTE_ADDR')
        # user.last_connect_date = datetime.now()
        # user.language = Language[language]
        # user.save()

        result = {}
        result['accessToken'] = accessToken
        result['accessKey'] = authKey
        # result['language'] = user.language.name

        return result
