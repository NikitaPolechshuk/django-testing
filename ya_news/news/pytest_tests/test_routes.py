import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.pytest_tests import settings


@pytest.mark.parametrize(
    'name, args',
    (
        (settings.NEWS_DETAIL_NAME,
         pytest.lazy_fixture('one_news_pk_for_arg')),
        (settings.NEWS_HOME_NAME, None),
        (settings.USER_LOGIN_NAME, None),
        (settings.USER_LOGOUT_NAME, None),
        (settings.USER_SIGNUP_NAME, None),
    ),
)
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
        parametrized_client, name, one_comment, expected_status
):
    """Проверка доступности страниц редактирования и удаления комментария."""
    url = reverse(name, args=(one_comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (settings.NEWS_DELETE_NAME,
     settings.NEWS_EDIT_NAME),
)
def test_redirect_for_anonymous_client(
    name, client, one_comment
):
    """Проверка редиректа при попытке анонимав
    зайти на страницу удаления/редактирования комментария.
    """
    login_url = reverse(settings.USER_LOGIN_NAME)
    url = reverse(name, args=(one_comment.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
