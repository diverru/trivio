import re
import logging


from django.conf import settings

from trivio_backend.core.utils import call_external_api

logger = logging.getLogger(__name__)

RE_EMAIL = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
HUNTER_VERIFIER_URL = "https://api.hunter.io/v2/email-verifier?email={email}&api_key={api_key}"
CLEARBIT_ENRICHMENT_URL = "https://person.clearbit.com/v1/people/email/{email}"


def verify_email(email):
    # hunter.io returns HTTP 400 for malformed emails, so let's filter them
    # regexp from https://emailregex.com
    if not RE_EMAIL.match(email):
        logger.info(f"email {email} is not matches generic email regexp")
        return False
    if settings.EMAIL_HUNTER_API_KEY is None:
        logger.warning("hunter.io api key is not specified, working without it")
        return True
    # see https://hunter.io/api/v2/docs#email-verifier
    data = call_external_api(
        url=HUNTER_VERIFIER_URL.format(email=email, api_key=settings.EMAIL_HUNTER_API_KEY),
        timeout=20,
    )
    if data is None:
        # it's better to send this case to sentry or something similar
        logger.info(f"problem of getting data from hunter.io")
        return False
    data = data["data"]

    return data["regexp"] and data["smtp_server"] and data["smtp_check"]


def enrich_email(email):
    if settings.CLEARBIT_API_KEY is None:
        return {}
    headers = {
        "Authorization": f"Bearer {settings.CLEARBIT_API_KEY}"
    }
    data = call_external_api(
        url=CLEARBIT_ENRICHMENT_URL.format(email=email),
        headers=headers,
    )
    return data or {}
