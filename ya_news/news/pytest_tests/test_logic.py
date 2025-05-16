import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests import settings


def test_anonymous_user_cant_create_comment(
    client, one_news,
):
    """Проверка что аноним не может создать комментарий."""
    url = reverse(settings.NEWS_DETAIL_NAME, args=(one_news.pk,))
    client.post(url, data={'text': settings.COMMENT_TEXT})
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client, author, one_news,
):
    """Проверка комментрирования авторизованным пользователем."""
    url = reverse(settings.NEWS_DETAIL_NAME, args=(one_news.pk,))
    response = author_client.post(url, data={'text': settings.COMMENT_TEXT})
    # Проверяем, что редирект привёл к разделу с комментами.
    assertRedirects(response, f'{url}#comments')
    # Проверяем что комментарий появился
    assert Comment.objects.count() == 1
    # Получаем объект комментария из базы.
    comment = Comment.objects.get()
    # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
    assert comment.text == settings.COMMENT_TEXT
    assert comment.news == one_news
    assert comment.author == author


@pytest.mark.parametrize(
    'bad_word',
    (BAD_WORDS),
)
def test_user_cant_use_bad_words(
    bad_word, author_client, one_news
):
    """Проверка использования плохих слов."""
    url = reverse(settings.NEWS_DETAIL_NAME, args=(one_news.pk,))
    response = author_client.post(url, data={'text': bad_word})
    form = response.context['form']
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )
    # Дополнительно убедимся, что комментарий не был создан.
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(one_comment, author_client):
    """Проверка удаления комментария автором."""
    delete_url = reverse(settings.NEWS_DELETE_NAME, args=(one_comment.pk,))
    response = author_client.delete(delete_url)
    # Проверяем, что редирект привёл к разделу с комментариями.
    url_to_comments = reverse(settings.NEWS_DETAIL_NAME,
                              args=(one_comment.pk,))
    assertRedirects(response, url_to_comments + '#comments')
    # Проверим статус-код ответа
    assert response.status_code == HTTPStatus.FOUND
    # Проверим количество комментариев стало 0
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        one_comment, not_author_client
):
    """Проверка что нельзя удалить комментарий не автором."""
    delete_url = reverse(settings.NEWS_DELETE_NAME, args=(one_comment.pk,))
    response = not_author_client.delete(delete_url)
    # Проверим статус-коды ответов.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Проверим количество комментариев не изменилось
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(one_news, one_comment, author_client, author):
    """Проверка редактирования комментария автором."""
    edit_url = reverse(settings.NEWS_EDIT_NAME, args=(one_comment.pk,))
    response = author_client.post(edit_url,
                                  data={'text': settings.NEW_COMMENT_TEXT})
    url_to_comments = reverse(settings.NEWS_DETAIL_NAME, args=(one_comment.pk,
                                                               ))
    assertRedirects(response, url_to_comments + '#comments')
    one_comment.refresh_from_db()
    # Проверяем, что в комментарии изменился только текст
    assert one_comment.text == settings.NEW_COMMENT_TEXT
    assert one_comment.author == author
    assert one_comment.news == one_news


def test_another_user_cant_edit_comment(
        one_news, one_comment, not_author_client, author
):
    """Проверка что нельзя редактировать комментарий не автором."""
    edit_url = reverse(settings.NEWS_EDIT_NAME, args=(one_comment.pk,))
    response = not_author_client.post(edit_url,
                                      data={'text': settings.NEW_COMMENT_TEXT})
    assert response.status_code == HTTPStatus.NOT_FOUND
    one_comment.refresh_from_db()
    # Проверяем, что cодержимое комментария не изменилось
    assert one_comment.text == settings.COMMENT_TEXT
    assert one_comment.author == author
    assert one_comment.news == one_news
