from django.test import TestCase
from django.urls import reverse

from crud.models import Task


class TaskCrudTests(TestCase):
    def setUp(self):
        self.task = Task.objects.create(title='Первая задача', description='Описание')

    def test_list_view(self):
        response = self.client.get(reverse('crud:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Первая задача')

    def test_detail_view(self):
        response = self.client.get(reverse('crud:task_detail', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Описание')

    def test_detail_not_found(self):
        response = self.client.get(reverse('crud:task_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_create_task(self):
        response = self.client.post(reverse('crud:task_create'), {
            'title': 'Новая задача',
            'description': 'Текст',
        })
        self.assertRedirects(response, reverse('crud:task_list'))
        self.assertTrue(Task.objects.filter(title='Новая задача').exists())

    def test_create_task_invalid(self):
        response = self.client.post(reverse('crud:task_create'), {'title': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 1)

    def test_update_task(self):
        response = self.client.post(
            reverse('crud:task_update', args=[self.task.id]),
            {'title': 'Изменено', 'description': 'Новое', 'is_done': 'on'},
        )
        self.assertRedirects(response, reverse('crud:task_detail', args=[self.task.id]))
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Изменено')
        self.assertTrue(self.task.is_done)

    def test_delete_task(self):
        response = self.client.post(reverse('crud:task_delete', args=[self.task.id]))
        self.assertRedirects(response, reverse('crud:task_list'))
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())
        