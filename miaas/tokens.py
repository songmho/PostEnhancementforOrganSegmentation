import time

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_actiavtion_hash(self, user_id, timestamp):
        return (
            six.text_type(user_id)+six.text_type(timestamp)
        )


if __name__ == '__main__':
    aat = AccountActivationTokenGenerator()
    print(aat.make_token())