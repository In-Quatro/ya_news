from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(
        url_detail,
        id_news_for_args,
        client,
        form_data
):
    """Проверяем, что анонимный пользователь не может отправить комментарий."""
    count_comments_before = Comment.objects.count()
    client.post(url_detail, data=form_data)
    count_comments_after = Comment.objects.count()
    assert count_comments_before == count_comments_after


def test_user_can_create_comment(
        url_detail,
        id_news_for_args,
        author_client,
        form_data,
        news,
        author
):
    """Проверяем, что авторизованный пользователь
    может отправить комментарий."""
    response = author_client.post(url_detail, data=form_data)
    assertRedirects(response, f'{url_detail}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(
        url_detail,
        admin_client,
        bad_words_data,
        id_news_for_args
):
    """Проверяем, что если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку."""
    count_comments_before = Comment.objects.count()
    response = admin_client.post(url_detail, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    count_comments_after = Comment.objects.count()
    assert count_comments_before == count_comments_after


def test_author_can_delete_comment(
        url_detail,
        url_delete,
        author_client,
        id_comment_for_args,
        id_news_for_args
):
    """Проверяем, что авторизованный пользователь может удалять
    свои комментарии."""
    count_comments_before = Comment.objects.count()
    response = author_client.post(url_delete)
    url_to_comments = url_detail + '#comments'
    assertRedirects(response, url_to_comments)
    count_comments_after = Comment.objects.count()
    assert count_comments_before - 1 == count_comments_after


def test_user_cant_delete_comment_of_another_user(
        url_delete,
        admin_client,
        id_comment_for_args
):
    """Проверяем, что авторизованный пользователь не может
    удалять чужие комментарии."""
    count_comments_before = Comment.objects.count()
    response = admin_client.post(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    count_comments_after = Comment.objects.count()
    assert count_comments_before == count_comments_after


def test_author_can_edit_comment(
        url_detail,
        url_edit,
        author_client,
        id_comment_for_args,
        form_data,
        id_news_for_args,
        comment,
        author,
        news
):
    """Проверяем, что авторизованный пользователь может
    редактировать свои комментарии."""
    comment_author_before = comment.author
    comment_news_before = comment.news
    response = author_client.post(url_edit, data=form_data)
    url_to_comments = url_detail + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    comment_text_after = comment.text
    comment_author_after = comment.author
    comment_news_after = comment.news
    assert comment_text_after == form_data['text']
    assert comment_author_before == comment_author_after
    assert comment_news_before == comment_news_after


def test_user_cant_edit_comment_of_another_user(
        url_edit,
        id_comment_for_args,
        admin_client,
        form_data,
        comment,
        author,
        news
):
    """Проверяем, что авторизованный пользователь не может
    редактировать чужие комментарии."""
    comment_text_before = comment.text
    comment_author_before = comment.author
    comment_news_before = comment.news
    response = admin_client.post(url_edit, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    comment_text_after = comment.text
    comment_author_after = comment.author
    comment_news_after = comment.news
    assert comment_text_before == comment_text_after
    assert comment_author_before == comment_author_after
    assert comment_news_before == comment_news_after
