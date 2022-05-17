from django.shortcuts import render


def handler404(request):
    return render(
        request=request,
        template_name='board/pages/404.html',
        status=404
    )
