"""Тесты маршрутов."""
from http import HTTPStatus

from django.contrib.auth import get_user_model

from notes.models import Note
from notes.tests.base_test_class import BaseTestClass

User = get_user_model()


class TestRoutes(BaseTestClass):
    """Проверка маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестирования."""
        super().setUpTestData()
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username=cls.authors_names[0])
        cls.reader = User.objects.create(username=cls.authors_names[1])
        # От имени author  создаём записку:
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.TEST_SLUG,
            author=cls.author,
        )

    def test_home_availability_for_anonymous_user(self):
        """Проверка доступности основных страниц анониму."""
        urls = (self.NOTES_HOME_URL,
                self.NOTES_LOGIN_URL,
                self.NOTES_LOGOUT_URL,
                self.NOTES_SIGNUP_URL,)
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code,
                                 HTTPStatus.OK)

    def test_availability_for_auth_user(self):
        """Проверка доступа авторизованного пользователю list, succes, add."""
        urls = (self.NOTES_LIST_URL,
                self.NOTES_SUCCESS_URL,
                self.NOTES_ADD_URL,)
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
        urls = (self.NOTES_DETAIL_URL,
                self.NOTES_EDIT_URL,
                self.NOTES_DELETE_URL,)
        for user, status in users_statuses:
            self.client.force_login(user)
            for url in urls:
                with self.subTest(user=user, url=url):
                    self.assertEqual(self.client.get(url).status_code,
                                     status)

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректа анонима при просмотре защищенных страниц."""
        urls = (self.NOTES_LIST_URL,
                self.NOTES_SUCCESS_URL,
                self.NOTES_ADD_URL,
                self.NOTES_DETAIL_URL,
                self.NOTES_EDIT_URL,
                self.NOTES_DELETE_URL)
        for url in urls:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url),
                                     self.REDIRECT_TEMPLATE.substitute(
                                         {'url': url})
                                     )
