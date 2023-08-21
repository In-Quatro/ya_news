import pytest

from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(
        url_home,
        client,
        some_news
):
    """Проверяем, что количество новостей на главной странице — не более 10."""
    response = client.get(url_home)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(
        url_home,
        client,
        some_news
):
    """Проверяем, что новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка."""
    response = client.get(url_home)
    object_list = response.context['object_list']
    all_dates = [comments.date for comments in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(
        url_detail,
        client,
        id_news_for_args,
        some_comments
):
    """Проверяем, что комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце."""
    response = client.get(url_detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = [comment.created for comment in news.comment_set.all()]
    sorted_comments = sorted(all_comments)
    assert all_comments == sorted_comments


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False)
     )
)
def test_pages_contains_form(
        url_detail,
        parametrized_client,
        id_news_for_args,
        news,
        form_in_context
):
    """Проверяем, что анонимному пользователю недоступна форма
    для отправки комментария на странице отдельной новости,
    а авторизованному доступна."""
    response = parametrized_client.get(url_detail)
    form = response.context.get('form')
    assert isinstance(form, CommentForm) is form_in_context
