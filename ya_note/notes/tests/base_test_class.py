import string

from django.urls import reverse
from django.test import TestCase


class BaseTestClass(TestCase):
    """Базовый класс тестирования. """

    TEST_SLUG = 'test-slug'

    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённый текст'

    NOTES_ADD_NAME = 'notes:add'
    NOTES_EDIT_NAME = 'notes:edit'
    NOTES_LOGIN_URL = reverse('users:login')
    NOTES_LOGOUT_URL = reverse('users:logout')
    NOTES_SIGNUP_URL = reverse('users:signup')
    NOTES_HOME_URL = reverse('notes:home')
    NOTES_SUCCESS_URL = reverse('notes:success')
    NOTES_LIST_URL = reverse('notes:list')
    NOTES_ADD_URL = reverse(NOTES_ADD_NAME)
    NOTES_DETAIL_URL = reverse('notes:detail',
                               kwargs={'slug': TEST_SLUG})
    NOTES_EDIT_URL = reverse(NOTES_EDIT_NAME,
                             kwargs={'slug': TEST_SLUG})
    NOTES_DELETE_URL = reverse('notes:delete',
                               kwargs={'slug': TEST_SLUG})

    # Шаблон редиректа
    REDIRECT_TEMPLATE = string.Template(
        NOTES_LOGIN_URL + '?next=$url'
    )

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестирования."""
        cls.authors_names = ('Лев Толстой', 'Вася Пупкин')
