import pytest

from datetime import datetime, timedelta

from django.utils import timezone
from django.test.client import Client

from news.models import News, Comment
from news.pytest_tests import settings


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(
        username=settings.AUTHOR_USER_NAME)


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(
        username=settings.NOT_AUTHOR_USER_NAME)


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def one_news():
    return News.objects.create(
        title='Заголовок одиночной новости',
        text='Текст одиночной новости',
    )


@pytest.fixture
def a_lot_of_news():
    # Создаём объекты новостей на 2е страницы пагинатора
    today = datetime.today()
    all_news = [
        News(
            title=f'{settings.NEWS_TITLE} {index}',
            text=settings.NEWS_TEXT,
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def one_news_pk_for_arg(one_news):
    return (one_news.pk,)


@pytest.fixture
def one_comment(one_news, author):
    return Comment.objects.create(
        news=one_news, author=author, text=settings.COMMENT_TEXT,
    )


@pytest.fixture
def a_lot_of_comments(one_news, author):
    now = timezone.now()
    # Создаём комментарии в цикле от имени author
    for index in range(settings.COMMENTS_COUNT):
        comment = Comment.objects.create(
            news=one_news,
            author=author,
            text=f'{settings.COMMENT_TEXT} {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        comment.save()
    return Comment.objects.all()
