from django.shortcuts import render


def handler500(request):
    return render(
        request=request,
        template_name='home/pages/500.html',
        status=500
    )
