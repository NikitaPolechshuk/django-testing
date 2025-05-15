import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
        (pytest.lazy_fixture('news_detail_name'),
         pytest.lazy_fixture('one_news_pk_for_arg')),
        (pytest.lazy_fixture('news_home_name'), None),
        (pytest.lazy_fixture('user_login_name'), None),
        (pytest.lazy_fixture('user_logout_name'), None),
        (pytest.lazy_fixture('user_signup_name'), None),
    ),
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name, args):
    """Проверка доступности главной и основных страниц анониму."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, a_lot_of_comments, expected_status
):
    """Проверка доступности страниц редактирования и удаления комментария."""
    url = reverse(name, args=(a_lot_of_comments.first().pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (pytest.lazy_fixture('news_delete_name'),
     pytest.lazy_fixture('news_edit_name')),
)
@pytest.mark.django_db
def test_redirect_for_anonymous_client(
    name, client, a_lot_of_comments, user_login_name
):
    """Проверка редиректа при попытке анонимав
    зайти на страницу удаления/редактирования комментария.
    """
    login_url = reverse(user_login_name)
    url = reverse(name, args=(a_lot_of_comments.first().pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
