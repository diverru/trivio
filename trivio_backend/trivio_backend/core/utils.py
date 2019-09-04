import logging
import requests
import requests.exceptions
import time

from rest_framework.permissions import BasePermission, SAFE_METHODS

logger = logging.getLogger(__name__)


def call_external_api(url, max_attempts=3, timeout=5, retry_interval=0.5, no_retry_status_codes=tuple(), **kwargs):
    for attempt in range(max_attempts):
        try:
            logger.info(f"calling API {url}, attempt {attempt + 1}")
            r = requests.get(url, timeout=timeout, **kwargs)
            if r.status_code == 200:
                logger.info(f"API call successful")
                return r.json()
            logger.info(f"got HTTP {r.status_code}")
            if r.status_code in no_retry_status_codes:
                return {}
        except requests.exceptions.RequestException:
            logger.exception('')
        logger.info("retrying")
        time.sleep(retry_interval)
        retry_interval *= 1.5
    logger.info("giving up to call API")
    return None


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
