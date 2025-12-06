import pytest
from django.urls import reverse, resolve
from tests.data.urls_user_data import user_urls
from tests.data.urls_shop_data import shop_urls
from tests.data.urls_admin_data import admin_urls


@pytest.mark.parametrize("url_name, view_func, kwargs, expected_status",
                         user_urls + shop_urls + admin_urls)
def test_url_resolves_correct_view(url_name, view_func, kwargs, expected_status):
    """
    Проверяет, что reverse(url_name, kwargs) соответствует правильному классу view.
    Если URL требует обязательные аргументы, подставляются фиктивные значения.
    """

    # Если kwargs не передан, создаём пустой словарь
    if not isinstance(kwargs, dict):
        kwargs = {}

    # Фиктивные значения для обязательных аргументов
    if url_name == "auth_password_reset_confirm":
        kwargs.setdefault("uidb64", "fakeuid")
        kwargs.setdefault("token", "faketoken")

    if url_name == "shop_product_detail":
        kwargs.setdefault("slug", "test-product")

    # Формируем URL
    url = reverse(url_name, kwargs=kwargs)
    resolved = resolve(url)

    # Проверка, что вью совпадает
    assert resolved.func.view_class == view_func, (
        f"{url_name}: ожидался {view_func.__name__}, "
        f"получен {resolved.func.view_class.__name__}"
    )

