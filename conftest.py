from datetime import datetime, timedelta

import pytest
from django.utils import timezone
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Фикстура с пользователем Автор."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    """Фиксткра с клиентом автора."""
    client.force_login(author)
    return client


@pytest.fixture
def news(author):
    """Фикстура с одной новостью."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def some_news(django_db_setup):
    """Фикстура с несколькими комментариями."""
    today = datetime.today()
    for index in range(20):
        News.objects.create(
            title=f'Заголовок {index}',
            text=f'Текст {index}',
            date=today - timedelta(days=index)
        )


@pytest.fixture
def comment(news, author):
    """Фикстура с одним комментарием к новости с Автором."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def some_comments(django_db_setup, news, author):
    """Фикстура с несколькими комментариями к новости с Автором."""
    now = timezone.now()
    for index in range(3):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
    )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def id_news_for_args(news):
    """Фикстура для reverse для args id новости."""
    return news.id,


@pytest.fixture
def id_comment_for_args(comment):
    """Фикстура для reverse для args id комментария."""
    return comment.id,
