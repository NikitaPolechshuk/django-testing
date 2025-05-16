import pytest

from django.urls import reverse

from news.forms import CommentForm
from news.pytest_tests import settings


def test_news_count(a_lot_of_news, client):
    """Проверка количества новостей на главной странице."""
    response = client.get(reverse(settings.NEWS_HOME_NAME))
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(a_lot_of_news, client):
    """Проверка сортировки новостей по дате."""
    response = client.get(reverse(settings.NEWS_HOME_NAME))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(one_news, a_lot_of_comments, client):
    """Проверка сортировки комментариев по дате."""
    response = client.get(reverse(settings.NEWS_DETAIL_NAME,
                                  args=(one_news.pk,)))
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, form_on_page',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_pages_contains_form(parametrized_client, form_on_page, one_news):
    """Проверка наличия/отсутсвия формы отправки комментария."""
    url = reverse(settings.NEWS_DETAIL_NAME, args=(one_news.pk,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_on_page
    if form_on_page:
        assert isinstance(response.context['form'], CommentForm)
