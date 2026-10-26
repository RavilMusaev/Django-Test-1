from django.shortcuts import render, get_object_or_404, redirect
from .forms import TaskForm
from .models import Task


def task_list(request):
    tasks = Task.objects.all().order_by('-id')
    return render(request, 'crud/task_list.html', {'tasks': tasks})


def task_detail(request, id):
    task = get_object_or_404(Task, id=id)
    return render(request, 'crud/task_detail.html', {'task': task})


def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('crud:task_list')
    else:
        form = TaskForm()
    return render(request, 'crud/task_form.html', {'form': form, 'title': 'Создать задачу'})


def task_update(request, id):
    task = get_object_or_404(Task, id=id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('crud:task_detail', id=task.id)
    else:
        form = TaskForm(instance=task)
    return render(request, 'crud/task_form.html', {'form': form, 'title': 'Редактировать задачу'})


def task_delete(request, id):
    task = get_object_or_404(Task, id=id)
    if request.method == 'POST':
        task.delete()
        return redirect('crud:task_list')
    return render(request, 'crud/task_confirm_delete.html', {'task': task})