from urllib import quote

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from djblets.auth.util import login_required
from djblets.siteconfig.models import SiteConfiguration
from djblets.util.decorators import simple_decorator

from reviewboard.accounts.models import Profile


@simple_decorator
def check_login_required(view_func):
    """
    A decorator that checks whether login is required on this installation
    and, if so, checks if the user is logged in. If login is required and
    the user is not logged in, they're redirected to the login link.
    """
    def _check(*args, **kwargs):
        siteconfig = SiteConfiguration.objects.get_current()

        if siteconfig.get("auth_require_sitewide_login"):
            return login_required(view_func)(*args, **kwargs)
        else:
            return view_func(*args, **kwargs)

    return _check


@simple_decorator
def valid_prefs_required(view_func):
    """
    A decorator that checks whether the user has completed the first-time
    setup by saving their preferences at least once. Redirects to the
    preferences URL if they have not.

    If the user is not logged in, this will do nothing. That allows it to
    be used with @check_login_required.
    """
    def _check_valid_prefs(request, *args, **kwargs):
        try:
            if (request.user.is_anonymous() or
                request.user.get_profile().first_time_setup_done):
                return view_func(request, *args, **kwargs)
        except Profile.DoesNotExist:
            pass

        return HttpResponseRedirect("%s?%s=%s" %
                                    (reverse("user-preferences"),
                                     REDIRECT_FIELD_NAME,
                                     quote(request.get_full_path())))

    return _check_valid_prefs
