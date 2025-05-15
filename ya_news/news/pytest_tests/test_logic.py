import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, one_news, comment_form_data, news_detail_name
):
    """Проверка что аноним не может создать комментарий."""
    url = reverse(news_detail_name, args=(one_news.pk,))
    client.post(url, data=comment_form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client, author, one_news, comment_form_data, news_detail_name
):
    """Проверка комментрирования авторизованным пользователем."""
    url = reverse(news_detail_name, args=(one_news.pk,))
    response = author_client.post(url, data=comment_form_data)
    # Проверяем, что редирект привёл к разделу с комментами.
    assertRedirects(response, f'{url}#comments')
    # Проверяем что комментарий появился
    assert Comment.objects.count() == 1
    # Получаем объект комментария из базы.
    comment = Comment.objects.get()
    # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
    assert comment.text == comment_form_data['text']
    assert comment.news == one_news
    assert comment.author == author


def test_user_cant_use_bad_words(
    author_client, one_news, comment_form_data, news_detail_name
):
    """Проверка использования плохих слов."""
    url = reverse(news_detail_name, args=(one_news.pk,))
    comment_form_data['text'] += BAD_WORDS[0]
    response = author_client.post(url, data=comment_form_data)
    form = response.context['form']
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )
    # Дополнительно убедимся, что комментарий не был создан.
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'parametrized_client, expected_status, expected_comments_count',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND, 1),
        (pytest.lazy_fixture('author_client'), HTTPStatus.FOUND, 0)
    ),
)
def test_delete_comment(
    parametrized_client, expected_status, expected_comments_count,
    one_comment, author_client, news_delete_name, news_detail_name
):
    """Проверка удаления комментария автором и другим пользователем."""
    delete_url = reverse(news_delete_name, args=(one_comment.pk,))
    response = parametrized_client.delete(delete_url)
    # Для автора проверяем, что редирект привёл к разделу с комментариями.
    if parametrized_client == author_client:
        url_to_comments = reverse(news_detail_name, args=(one_comment.pk,))
        assertRedirects(response, url_to_comments + '#comments')
    # Проверим статус-коды ответов.
    assert response.status_code == expected_status
    # Проверим количество комментариев
    assert Comment.objects.count() == expected_comments_count


@pytest.mark.parametrize(
    'parametrized_client, expected_data',
    (
        (pytest.lazy_fixture('not_author_client'),
         pytest.lazy_fixture('comment_form_data')),
        (pytest.lazy_fixture('author_client'),
         pytest.lazy_fixture('new_comment_form_data'))
    ),
)
def test_edit_comment(
    parametrized_client, expected_data,
    one_comment, author_client, new_comment_form_data,
    news_detail_name, news_edit_name
):
    """Проверка редактирования комментария автором и другим пользователем."""
    edit_url = reverse(news_edit_name, args=(one_comment.pk,))
    response = parametrized_client.post(edit_url, data=new_comment_form_data)
    # Для автора проверяем, что редирект привёл к разделу с комментариями.
    if parametrized_client == author_client:
        url_to_comments = reverse(news_detail_name, args=(one_comment.pk,))
        assertRedirects(response, url_to_comments + '#comments')
    else:
        # Для не автора проверяем, что вернулась 404 ошибка.
        assert response.status_code == HTTPStatus.NOT_FOUND
    # Обновляем объект комментария.
    one_comment.refresh_from_db()
    # Проверяем текст комментария
    assert one_comment.text == expected_data['text']
