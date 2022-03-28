from django.shortcuts import render
from library.methods.helper import Helper

from .forms import IndexForm, RegisterForm

#from .models import User  # noqa: E265


def handler404(request):
    return render(
        request=request,
        template_name='home/pages/404.html',
        status=404
    )


def index(request):
    if request.method == 'GET':
        return render(
            request=request,
            template_name='home/pages/index.html'
        )
    elif request.method == 'POST':
        form = IndexForm(request.POST)
        print(form)
        return render(
            request=request,
            template_name='home/pages/index.html'
        )


def register(request):
    if request.method == 'GET':
        """ result = User.objects.all()[0]
        context = {
            'form': result
        } """
        return render(
            request=request,
            template_name='home/pages/register.html'
        )
    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.use_password = Helper().hash_gen(obj.use_password)
            obj.use_status = 1
            obj.save()

        return render(
            request=request,
            template_name='home/pages/register.html'
        )
