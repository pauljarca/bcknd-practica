import logging
import os
from urllib.parse import urlparse

from django.contrib.sites.models import Site
from django.conf import settings

log = logging.getLogger('setsitename')
logging.basicConfig(level=logging.INFO)


SITE_NAME = os.getenv('DJANGO_SITE_NAME', 'Practica AC')
SITE_DOMAIN = urlparse(settings.EXTERNAL_URL).hostname


def fmtsite(name: str, domain: str) -> str:
    return f"'{name} <{domain}>'"


try:
    site = Site.objects.filter(pk=settings.SITE_ID).get()
    old_name, old_domain = site.name, site.domain

    if old_name != SITE_NAME or old_domain != SITE_DOMAIN:
        site.name = SITE_NAME
        site.domain = SITE_DOMAIN
        site.save(update_fields=['name', 'domain'])
        log.info(f"changed default site (SITE_ID={settings.SITE_ID}) to "
                 f"{fmtsite(SITE_NAME, SITE_DOMAIN)} (was {fmtsite(old_name, old_domain)})")
    else:
        log.info(f"default site {fmtsite(SITE_NAME, SITE_DOMAIN)} (SITE_ID={settings.SITE_ID}) was not changed")

except (Site.DoesNotExist, Site.MultipleObjectsReturned):
    log.error(f"site with SITE_ID={settings.SITE_ID} does not exist", exc_info=True)
