import pytest

from django.conf import settings
from django.urls import reverse

HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count(client, some_news):
    """Проверяем что на главной странице отображается не больше 10 новостей."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    new_count = len(object_list)
    assert new_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, some_news):
    """Проверяем что новости выведены на странице от новых к старым."""
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [comments.date for comments in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, id_news_for_args, some_comments):
    """
    Проверяем что комментарии на странице с новостью
    отображаются от старых к новым.
    """
    url = reverse('news:detail', args=id_news_for_args)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[2].created


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
    (pytest.lazy_fixture('author_client'), True),
    (pytest.lazy_fixture('client'), False)
     )
)
def test_pages_contains_form(
        parametrized_client, id_news_for_args, news, form_in_context):
    """
    Проверяем наличие формы для комментария на подробной странице новости
    у авторизованного и не авторизованного пользователя.
    """
    url = reverse('news:detail', args=id_news_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_context
