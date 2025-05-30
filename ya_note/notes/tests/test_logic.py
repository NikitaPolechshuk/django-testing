"""Проверка логики."""
from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client

from notes.forms import WARNING
from notes.models import Note
from notes.tests.base_test_class import BaseTestClass

User = get_user_model()


class TestCommentCreation(BaseTestClass):
    """Проверка создания записи."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестирования."""
        super().setUpTestData()
        # Создаём клиент для auhor, логинимся в клиенте.
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        # Создадим одну запись в БД от имени author без указания slug
        cls.note_data = {'title': cls.NOTE_TITLE,
                         'text': cls.NOTE_TEXT,
                         'author': cls.author}
        cls.note = Note.objects.create(title=cls.note_data['title'],
                                       text=cls.note_data['text'],
                                       author=cls.note_data['author'])
        # Подготовим форму для отправки еще одной записи без поля slug
        # заголовок изменим, добавим _new в конце
        cls.form_data_empty_slug = {'title': cls.NOTE_TITLE + '_new',
                                    'text': cls.NOTE_TEXT}

    def setUp(self):
        """Будем запоминать текущее количество записей в БД."""
        self.start_notes_count = Note.objects.count()

    def test_anonymous_user_cant_create_note(self):
        """Проверка что аноним не может создать запись."""
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы записи.
        self.client.post(self.NOTES_ADD_URL, data=self.form_data_empty_slug)
        # Ожидаем, что количество записей в базе не изменится
        self.assertEqual(Note.objects.count(),
                         self.start_notes_count)

    def test_authorized_can_create_note(self):
        """Проверка возможности оставлять записи авторизованным юзерам."""
        # Дополним данные для формы полем slug
        form_data = self.form_data_empty_slug
        form_data['slug'] = self.TEST_SLUG
        # Совершаем запрос через авторизованный клиент.
        response = self.author_client.post(self.NOTES_ADD_URL,
                                           data=form_data)
        # Проверяем, что редирект привёл к странице успешного добавления
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)
        # Убеждаемся, что записей теперь на 1шт больше
        self.assertEqual(Note.objects.count(),
                         self.start_notes_count + 1)
        new_note = Note.objects.last()
        # Проверяем, что все атрибуты новой записи совпадают с ожидаемыми.
        self.assertEqual(new_note.title, form_data['title'])
        self.assertEqual(new_note.text, form_data['text'])
        self.assertEqual(new_note.slug, form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_correct_slug(self):
        """Проверка правильности формирования slug из title."""
        # Совершаем запрос через авторизованный клиент author.
        response = self.author_client.post(self.NOTES_ADD_URL,
                                           data=self.form_data_empty_slug)
        # Проверяем, что редирект привёл к странице успешного добавления
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)
        # Убеждаемся, что записей теперь на 1шт больше
        self.assertEqual(Note.objects.count(),
                         self.start_notes_count + 1)
        # Получаем добавленный объект записи из базы.
        note = Note.objects.last()
        # Проверяем, что все атрибуты записи совпадают с ожидаемыми.
        # Хотя можно вроде повтороно эти поля не проверять, но мало ли
        # при автозаполнение поля slug происходят сбои с другими полями.
        self.assertEqual(note.title, self.form_data_empty_slug['title'])
        self.assertEqual(note.text, self.form_data_empty_slug['text'])
        self.assertEqual(note.author, self.author)
        # Проверяем что slug правильно сформирован из заголовка
        self.assertEqual(note.slug,
                         slugify(self.form_data_empty_slug['title']))

    def test_cannot_create_note_with_same_slug(self):
        """Проверка не возможности создать заметку с одинаковым slug."""
        # Отправим POST запрос с такими же данными что в фикстуре
        response = self.author_client.post(self.NOTES_ADD_URL,
                                           data=self.note_data)
        form = response.context['form']
        # Проверим что форма вернула ошибку
        self.assertFormError(form, 'slug', Note.objects.last().slug + WARNING)
        # Убеждаемся, что их количество записей не изменилось
        self.assertEqual(Note.objects.count(),
                         self.start_notes_count)


class TestNoteEditDelete(BaseTestClass):
    """Проверка редактирования и удаления записей."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Создаём клиентов для пользователей и залогинимся
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Создадим запись от имени автора
        cls.note = Note.objects.create(title=cls.NOTE_TITLE,
                                       text=cls.NOTE_TEXT,
                                       slug=cls.TEST_SLUG,
                                       author=cls.author)
        # Формируем данные для POST-запроса по обновлению записи.
        cls.form_data = {'title': cls.NOTE_TITLE, 'text': cls.NEW_NOTE_TEXT}

    def setUp(self):
        """Будем запоминать текущее количество записей в БД."""
        self.notes_count = Note.objects.count()

    def test_author_can_delete_note(self):
        """Проверка удаления записи автором."""
        # От имени автора отправляем DELETE-запрос на удаление.
        response = self.author_client.delete(self.NOTES_DELETE_URL)
        # Проверяем, что редирект привёл на страницу успешного удаления.
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)
        # Заодно проверим статус-коды ответов.
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        # Ожидаем на одну запись меньше в системе.
        self.assertEqual(Note.objects.count(),
                         self.notes_count - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Проверка что нельзя удалить запись не автором."""
        # Выполняем запрос на удаление от пользователя-читателя.
        response = self.reader_client.delete(self.NOTES_DELETE_URL)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что записи по-прежнему на месте.
        self.assertEqual(Note.objects.count(),
                         self.notes_count)

    def test_author_can_edit_note(self):
        """Проверка редактирования записи автором."""
        # Выполняем запрос на редактирование от имени автора записи.
        response = self.author_client.post(self.NOTES_EDIT_URL,
                                           data=self.form_data)
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, self.NOTES_SUCCESS_URL)
        # Обновляем объект записи.
        self.note.refresh_from_db()
        # Проверяем, что текст записи соответствует обновленному.
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        """Проверка что нельзя редактировать запись не автором."""
        # Выполняем запрос на редактирование от имени другого пользователя.
        response = self.reader_client.post(self.NOTES_EDIT_URL,
                                           data=self.form_data)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект записи.
        self.note.refresh_from_db()
        # Проверяем, что текст остался тем же, что и был.
        self.assertEqual(self.note.text, self.NOTE_TEXT)
