# Тут сохраним константы
from django.conf import settings


NEWS_COUNT_ON_HOME_PAGE = settings.NEWS_COUNT_ON_HOME_PAGE

AUTHOR_USER_NAME = 'Автор'
NOT_AUTHOR_USER_NAME = 'Не автор'

COMMENTS_COUNT = 10
COMMENT_TEXT = 'Tекст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'

NEWS_TITLE = 'Новость'
NEWS_TEXT = 'Текст новости'

NEWS_HOME_NAME = 'news:home'
NEWS_DETAIL_NAME = 'news:detail'
NEWS_EDIT_NAME = 'news:edit'
NEWS_DELETE_NAME = 'news:delete'

USER_LOGIN_NAME = 'users:login'
USER_LOGOUT_NAME = 'users:logout'
USER_SIGNUP_NAME = 'users:signup'
