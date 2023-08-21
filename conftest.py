from datetime import datetime, timedelta

import pytest
from django.utils import timezone
from django.urls import reverse

from news.models import Comment, News
from news.forms import BAD_WORDS


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


@pytest.fixture
def form_data():
    """Фикстура для передачи формы комментария."""
    return {
        'text': 'Новый текст комментария'
    }


@pytest.fixture
def bad_words_data():
    """Фикстура для передачи формы запрещенных слов в комментариях."""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    return bad_words_data


@pytest.fixture
def url_home():
    return reverse('news:home')


@pytest.fixture
def url_detail(id_news_for_args):
    return reverse('news:detail', args=id_news_for_args)


@pytest.fixture
def url_edit(id_comment_for_args):
    return reverse('news:edit', args=id_comment_for_args)


@pytest.fixture
def url_delete(id_comment_for_args):
    return reverse('news:delete', args=id_comment_for_args)


@pytest.fixture
def url_login():
    return reverse('users:login')


@pytest.fixture
def url_logout():
    return reverse('users:logout')


@pytest.fixture
def url_signup():
    return reverse('users:signup')
