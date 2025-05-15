"""Тесты контента."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from notes.models import Note
from notes.forms import NoteForm

NOTES_LIST_URL = reverse('notes:list')
NOTES_ADD_NAME = 'notes:add'
NOTES_EDIT_NAME = 'notes:edit'

User = get_user_model()


class TestPages(TestCase):
    """Проверка страниц."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестирования."""
        cls.authors_names = ('Лев Толстой', 'Вася Пупкин')
        cls.authors = []
        cls.notes = []
        # Создадим по одной заметки от каждого из двух авторов
        for author_name in cls.authors_names:
            current_author = User.objects.create(username=author_name)
            cls.authors.append(current_author)
            cls.notes.append(Note.objects.create(
                title='Заголовок ' + author_name,
                text='Текст заметки',
                author=current_author,
            ))

    def test_notes(self):
        """Проверка что записи на странице list передаются в object_list
        И проверка что отображаются только записи автора.
        """
        # Логинимся первым пользователем и загружаем список заметок
        self.client.force_login(self.authors[0])
        response = self.client.get(NOTES_LIST_URL)
        # Проверка что object_list существует
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        # Определяем количество записей в списке.
        count = object_list.count()
        # Проверяем, что на странице одна запись
        self.assertEqual(count, 1)
        # Проверяем что запись пренадлежит юзеру
        self.assertEqual(object_list[0].author, self.authors[0])

    def test_authorized_client_has_form(self):
        """Проверка наличия формы на страницах создания и редактирования.
        Для проверки используем первого юзера и его первую заметку
        """
        urls = ((NOTES_ADD_NAME, None),
                (NOTES_EDIT_NAME, (self.notes[0].slug, )),
                )
        # Авторизуем клиент при помощи первого пользователя.
        self.client.force_login(self.authors[0])
        for name, args in urls:
            with self.subTest(name=name, args=args):
                response = self.client.get(reverse(name, args=args))
                # Проверка наличия формы
                self.assertIn('form', response.context)
                # Проверим, что объект формы соответствует классу
                self.assertIsInstance(response.context['form'], NoteForm)
