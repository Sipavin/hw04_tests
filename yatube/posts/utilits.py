from django.core.paginator import Paginator
from django import forms


def paginator(request, post_list, QTY=10):
    paginator = Paginator(post_list, QTY)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def validate_not_empty(value):
    if value == '':
        raise forms.ValidationError(
            'Поле не может быть пустым',
            params={'value': value},
        )
