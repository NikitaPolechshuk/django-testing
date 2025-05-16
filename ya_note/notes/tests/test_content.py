"""Тесты контента."""
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm
from notes.tests.base_test_class import BaseTestClass


User = get_user_model()


class TestPages(BaseTestClass):
    """Проверка страниц."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Создадим по одной заметки от каждого из двух юзер
        cls.author_note = Note.objects.create(
            title=cls.NOTE_TITLE + cls.AUTHOR_NAME,
            text=cls.NOTE_TEXT,
            author=cls.author,
        )
        cls.reader_note = Note.objects.create(
            title=cls.NOTE_TITLE + cls.READER_NAME,
            text=cls.NOTE_TEXT,
            author=cls.reader,
        )

    def test_notes(self):
        """Проверка что записи на странице list передаются в object_list
        И проверка что отображаются только записи автора.
        """
        # Логинимся пользователем author и загружаем список заметок
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST_URL)
        # Проверка что object_list существует
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        # Определяем количество записей в списке.
        count = object_list.count()
        # Проверяем, что на странице одна запись
        self.assertEqual(count, 1)
        # Проверяем что запись пренадлежит юзеру
        self.assertEqual(object_list[0].author, self.author)

    def test_authorized_client_has_form(self):
        """Проверка наличия формы на страницах создания и редактирования.
        Для проверки используем author и его заметку
        """
        urls = ((self.NOTES_ADD_NAME, None),
                (self.NOTES_EDIT_NAME, (self.author_note.slug, )),
                )
        # Авторизуем клиент при помощи пользователя author.
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name, args=args):
                response = self.client.get(reverse(name, args=args))
                # Проверка наличия формы
                self.assertIn('form', response.context)
                # Проверим, что объект формы соответствует классу
                self.assertIsInstance(response.context['form'], NoteForm)
