from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse

from blog.models import Blog


class BlogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.blog = Blog.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание для проверки блога',
            image='blog/test_image.jpg',
            author='Тестовый Автор',
        )

    # ---------- Модель ----------
    def test_blog_model_creation(self):
        self.assertEqual(self.blog.title, 'Тестовый заголовок')
        self.assertEqual(self.blog.author, 'Тестовый Автор')
        self.assertEqual(str(self.blog), 'Тестовый заголовок')

    def test_new_blog_has_zero_likes(self):
        self.assertEqual(self.blog.likes, 0)

    # ---------- List ----------
    def test_blog_list_view(self):
        response = self.client.get(reverse('blog_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog_list.html')
        self.assertContains(response, 'Тестовый заголовок')

    def test_blog_list_context_contains_blog(self):
        response = self.client.get(reverse('blog_list'))

        self.assertIn(self.blog, response.context['blog'])

    def test_blog_list_empty(self):
        Blog.objects.all().delete()
        response = self.client.get(reverse('blog_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['blog']), 0)
        self.assertNotContains(response, 'Тестовый заголовок')

    def test_blog_list_ordering_newest_first(self):
        newer = Blog.objects.create(
            title='Новый пост', description='...', image='blog/new.jpg'
        )
        response = self.client.get(reverse('blog_list'))

        self.assertEqual(list(response.context['blog']), [newer, self.blog])

    def test_blog_list_has_link_to_detail(self):
        response = self.client.get(reverse('blog_list'))
        detail_url = reverse('blog_detail', args=[self.blog.id])

        self.assertContains(response, f'href="{detail_url}"')

    def test_blog_list_link_leads_to_detail(self):
        detail_url = reverse('blog_detail', args=[self.blog.id])
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, 200)

    # ---------- Detail ----------
    def test_blog_detail_view(self):
        response = self.client.get(reverse('blog_detail', args=[self.blog.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog_detail.html')

    def test_blog_detail_content(self):
        response = self.client.get(reverse('blog_detail', args=[self.blog.id]))

        self.assertContains(response, 'Тестовый заголовок')
        self.assertContains(response, 'Тестовое описание для проверки блога')
        self.assertContains(response, 'Тестовый Автор')

    def test_blog_detail_context_has_correct_id(self):
        response = self.client.get(reverse('blog_detail', args=[self.blog.id]))

        self.assertEqual(response.context['blog_id'].id, self.blog.id)

    def test_blog_detail_not_found(self):
        response = self.client.get(reverse('blog_detail', args=[999]))

        self.assertEqual(response.status_code, 404)

    def test_blog_detail_server_error(self):
        client = Client(raise_request_exception=False)
        url = reverse('blog_detail', args=[self.blog.id])
        with patch('blog.views.get_object_or_404', side_effect=Exception('boom')):
            response = client.get(url)

        self.assertEqual(response.status_code, 500)

    def test_author_display_with_rank(self):
        default_blog = Blog.objects.create(
            title='Пост Иванова',
            description='Текст....',
            image='blog/test.jpg',
        )
        response = self.client.get(reverse('blog_detail', args=[default_blog.id]))

        self.assertContains(response, 'Ivanov Ivan (Главный редактор)')

    # ---------- Лайки / просмотры ----------
    def test_likes_increase_on_detail_view(self):
        self.client.get(reverse('blog_detail', args=[self.blog.id]))
        self.blog.refresh_from_db()

        self.assertEqual(self.blog.likes, 1)

    def test_likes_increase_on_each_visit(self):
        url = reverse('blog_detail', args=[self.blog.id])
        self.client.get(url)
        self.client.get(url)
        self.blog.refresh_from_db()

        self.assertEqual(self.blog.likes, 2)

    def test_likes_not_changed_by_list_view(self):
        self.client.get(reverse('blog_list'))
        self.blog.refresh_from_db()

        self.assertEqual(self.blog.likes, 0)

    def test_likes_of_other_blog_not_changed(self):
        other = Blog.objects.create(
            title='Другой', description='...', image='blog/other.jpg'
        )
        self.client.get(reverse('blog_detail', args=[self.blog.id]))
        other.refresh_from_db()

        self.assertEqual(other.likes, 0)