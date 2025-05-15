import pytest

from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(a_lot_of_news, client, news_home_name):
    """Проверка количества новостей на главной странице."""
    response = client.get(reverse(news_home_name))
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(a_lot_of_news, client, news_home_name):
    """Проверка сортировки новостей по дате."""
    response = client.get(reverse(news_home_name))
    object_list = response.context['object_list']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(one_news, a_lot_of_comments, client, news_detail_name):
    """Проверка сортировки комментариев по дате."""
    response = client.get(reverse(news_detail_name, args=(one_news.pk,)))
    # Проверяем, что объект новости находится в словаре контекста
    # под ожидаемым именем - названием модели.
    assert 'news' in response.context
    # Получаем объект новости.
    news = response.context['news']
    # Получаем все комментарии к новости.
    all_comments = news.comment_set.all()
    # Собираем временные метки всех комментариев.
    all_timestamps = [comment.created for comment in all_comments]
    # Сортируем временные метки, менять порядок сортировки не надо.
    sorted_timestamps = sorted(all_timestamps)
    # Проверяем, что временные метки отсортированы правильно.
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_on_page',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_pages_contains_form(parametrized_client, form_on_page, one_news):
    """Проверка наличия/отсутсвия формы отправки комментария."""
    # Формируем URL.
    url = reverse('news:detail', args=(one_news.pk,))
    # Запрашиваем нужную страницу:
    response = parametrized_client.get(url)
    # Проверяем, должна ли быть форма в словаре контекста:
    assert ('form' in response.context) is form_on_page
    # Проверяем, что объект формы относится к нужному классу.
    if form_on_page:
        assert isinstance(response.context['form'], CommentForm)
