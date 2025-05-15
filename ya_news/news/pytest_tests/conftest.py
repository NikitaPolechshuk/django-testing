import pytest

from datetime import datetime, timedelta

from django.utils import timezone
from django.test.client import Client
from django.conf import settings

from news.models import News, Comment


AUTHOR_USER_NAME = 'Автор'
NOT_AUTHOR_USER_NAME = 'Не автор'

COMMENTS_COUNT = 10
COMMENT_TEXT = 'Tекст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'

NEWS_TITLE = 'Новость'
NEWS_TEXT = 'Просто текст'

NEWS_HOME_NAME = 'news:home'
NEWS_DETAIL_NAME = 'news:detail'
NEWS_EDIT_NAME = 'news:edit'
NEWS_DELETE_NAME = 'news:delete'

USER_LOGIN_NAME = 'users:login'
USER_LOGOUT_NAME = 'users:logout'
USER_SIGNUP_NAME = 'users:signup'


@pytest.fixture
def news_home_name():
    return NEWS_HOME_NAME


@pytest.fixture
def news_detail_name():
    return NEWS_DETAIL_NAME


@pytest.fixture
def news_edit_name():
    return NEWS_EDIT_NAME


@pytest.fixture
def news_delete_name():
    return NEWS_DELETE_NAME


@pytest.fixture
def user_login_name():
    return USER_LOGIN_NAME


@pytest.fixture
def user_logout_name():
    return USER_LOGOUT_NAME


@pytest.fixture
def user_signup_name():
    return USER_SIGNUP_NAME


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username=AUTHOR_USER_NAME)


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username=NOT_AUTHOR_USER_NAME)


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
            title=f'{NEWS_TITLE} {index}',
            text=NEWS_TEXT,
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def one_news_pk_for_arg(one_news):
    return (one_news.pk,)


@pytest.fixture
def one_comment(one_news, author):
    return Comment.objects.create(
        news=one_news, author=author, text=COMMENT_TEXT,
    )


@pytest.fixture
def a_lot_of_comments(one_news, author):
    now = timezone.now()
    # Создаём комментарии в цикле от имени author
    for index in range(COMMENTS_COUNT):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=one_news, author=author, text=f'{COMMENT_TEXT} {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()
    return Comment.objects.all()


@pytest.fixture
def comment_form_data():
    return {
        'text': COMMENT_TEXT,
    }


@pytest.fixture
def new_comment_form_data():
    return {
        'text': NEW_COMMENT_TEXT,
    }
