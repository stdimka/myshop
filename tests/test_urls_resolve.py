import pytest
from django.urls import reverse, resolve
from tests.data.urls_user_data import user_urls
from tests.data.urls_shop_data import shop_urls
from tests.data.urls_admin_data import admin_urls


@pytest.mark.parametrize("url_name, view_func, kwargs, expected_status",
                         user_urls + shop_urls + admin_urls)
def test_url_resolves_correct_view(url_name, view_func, kwargs, expected_status):
    """
    Проверяет, что reverse(url_name) соответствует правильному классу view.
    """

    if isinstance(kwargs, dict):
        url = reverse(url_name, kwargs=kwargs)
    else:
        url = reverse(url_name)
    resolved = resolve(url)

    assert resolved.func.view_class == view_func, (
        f"{url_name}: ожидался {view_func.__name__}, "
        f"получен {resolved.func.view_class.__name__}"
    )
