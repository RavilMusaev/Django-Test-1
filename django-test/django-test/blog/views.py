from django.db.models import F
from django.shortcuts import render, get_object_or_404
from . import models


def blog_list_view(request):
    blog = models.Blog.objects.all().order_by('-id')
    return render(request, template_name='blog_list.html', context={'blog': blog})


def blog_detail_view(request, id):
    blog_id = get_object_or_404(models.Blog, id=id)
    models.Blog.objects.filter(id=id).update(likes=F('likes') + 1)
    blog_id.refresh_from_db()
    return render(request, template_name='blog_detail.html', context={'blog_id': blog_id})