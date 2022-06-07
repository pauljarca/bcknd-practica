from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ExportApplicantTokenGenerator(PasswordResetTokenGenerator):
    key_salt = "practica.ExportApplicantTokenGenerator"

    def make_token(self, company):
        # hack to prolong the timeout without overriding check_token
        ts = self._num_seconds(self._now())
        ts = ts + (settings.APPLICANT_EXPORT_TIMEOUT_DAYS - settings.PASSWORD_RESET_TIMEOUT_DAYS)
        return self._make_token_with_timestamp(company, ts)

    def check_token(self, company, token):
        # metohd overriden just to rename parameter
        return super().check_token(company, token)

    def _make_hash_value(self, company, timestamp):
        # this class (ab)uses the fact that PasswordResetTokenGenerator only uses the 'user' argument inside
        # _make_hash_value, allowing it to actually be any type of object if this method is properly overwritten
        return str(company.pk) + str(timestamp)


default_export_token_generator = ExportApplicantTokenGenerator()
