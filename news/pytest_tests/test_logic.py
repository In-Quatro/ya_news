from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(
        id_news_for_args,
        client,
        form_data
):
    """Проверяем, что анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=id_news_for_args)
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        id_news_for_args,
        author_client,
        form_data,
        news,
        author
):
    """
    Проверяем, что авторизованный пользователь
    может отправить комментарий.
    """
    url = reverse('news:detail', args=id_news_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(
        admin_client,
        bad_words_data,
        id_news_for_args
):
    """
    Проверяем, что если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=id_news_for_args)
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
        author_client,
        id_comment_for_args,
        id_news_for_args
):
    """
    Проверяем, что авторизованный пользователь может удалять свои комментарии.
    """
    news_url = reverse('news:detail', args=id_news_for_args)
    url = reverse('news:delete', args=id_comment_for_args)
    response = author_client.post(url)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        admin_client,
        id_comment_for_args
):
    """
    Проверяем, что авторизованный пользователь не может
    удалять чужие комментарии.
    """
    edit_url = reverse('news:delete', args=id_comment_for_args)
    response = admin_client.post(edit_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client,
        id_comment_for_args,
        form_data,
        id_news_for_args,
        comment
):
    """
    Проверяем, что авторизованный пользователь может
    редактировать свои комментарии.
    """
    news_url = reverse('news:detail', args=id_news_for_args)
    edit_url = reverse('news:edit', args=id_comment_for_args)
    response = author_client.post(edit_url, data=form_data)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        id_comment_for_args,
        admin_client,
        form_data,
        comment
):
    """
    Проверяем, что авторизованный пользователь не может
    редактировать чужие комментарии.
    """
    text_comment = comment.text
    edit_url = reverse('news:edit', args=id_comment_for_args)
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == text_comment
