"""Тесты маршрутов."""
import string

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

NOTE_TITLE = 'Заголовок'
NOTE_TEXT = 'Текст заметки'

TEST_SLUG = 'test-slug'

NOTES_LOGIN_URL = reverse('users:login')
NOTES_LOGOUT_URL = reverse('users:logout')
NOTES_SIGNUP_URL = reverse('users:signup')
NOTES_HOME_URL = reverse('notes:home')
NOTES_SUCCESS_URL = reverse('notes:success')
NOTES_LIST_URL = reverse('notes:list')
NOTES_ADD_URL = reverse('notes:add')
NOTES_DETAIL_URL = reverse('notes:detail',
                           kwargs={'slug': TEST_SLUG})
NOTES_EDIT_URL = reverse('notes:edit',
                         kwargs={'slug': TEST_SLUG})
NOTES_DELETE_URL = reverse('notes:delete',
                           kwargs={'slug': TEST_SLUG})

# Шаблон редиректа
REDIRECT_TEMPLATE = string.Template(
    NOTES_LOGIN_URL + '?next=$url'
)

User = get_user_model()


class TestRoutes(TestCase):
    """Проверка маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестирования."""
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        # От имени author  создаём записку:
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=TEST_SLUG,
            author=cls.author,
        )

    def test_home_availability_for_anonymous_user(self):
        """Проверка доступности основных страниц анониму."""
        urls = (NOTES_HOME_URL,
                NOTES_LOGIN_URL,
                NOTES_LOGOUT_URL,
                NOTES_SIGNUP_URL,)
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code,
                                 HTTPStatus.OK)

    def test_availability_for_auth_user(self):
        """Проверка доступа авторизованного пользователю list, succes, add."""
        urls = (NOTES_LIST_URL,
                NOTES_SUCCESS_URL,
                NOTES_ADD_URL,)
        self.client.force_login(self.author)
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code,
                                 HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """Проверка доступности страниц редактирования и удаления автору записи
        и невозможности другим пользователям.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (NOTES_DETAIL_URL,
                NOTES_EDIT_URL,
                NOTES_DELETE_URL,)
        for user, status in users_statuses:
            self.client.force_login(user)
            for url in urls:
                with self.subTest(user=user, url=url):
                    self.assertEqual(self.client.get(url).status_code,
                                     status)

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректа анонима при просмотре защищенных страниц."""
        urls = (NOTES_LIST_URL,
                NOTES_SUCCESS_URL,
                NOTES_ADD_URL,
                NOTES_DETAIL_URL,
                NOTES_EDIT_URL,
                NOTES_DELETE_URL)
        for url in urls:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url),
                                     REDIRECT_TEMPLATE.substitute({'url': url})
                                     )
