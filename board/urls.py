from django.urls import path

from board.views import (error_view, index_view, js_ajax,
                         labels_beneficiaries_form_view,
                         labels_beneficiaries_view,
                         labels_categories_form_view, labels_categories_view,
                         labels_clients_form_view, labels_clients_view,
                         labels_financial_form_view, labels_financial_view,
                         profile_password_view, profile_view)

app_name = 'board'

urlpatterns = [
    # INDEX
    path('board/index/', index_view.BoardIndexView.as_view()),
    path('board/', index_view.BoardIndexView.as_view(), name='index'),

    path(
        'board/index/new/',
        index_view.BoardIndexView.as_view(),
        name='index_new'
    ),

    path(
        'board/index/edit/',
        index_view.BoardIndexView.as_view(),
        name='index_edit'
    ),

    path(
        'board/index/delete/',
        index_view.BoardIndexView.as_view(),
        name='index_delete'
    ),

    # LABELS/BENEFICIARIES
    path(
        'board/labels/beneficiaries/',
        labels_beneficiaries_view.LabelsBeneficiariesView.as_view(),
        name='labels_beneficiaries'
    ),

    path(
        'board/labels/beneficiaries/edit/',
        labels_beneficiaries_view.LabelsBeneficiariesView.as_view(),
        name='labels_beneficiaries_edit'
    ),

    path(
        'board/labels/beneficiaries/delete/',
        labels_beneficiaries_view.LabelsBeneficiariesView.as_view(),
        name='labels_beneficiaries_delete'
    ),

    # LABELS/BENEFICIARIES/FORM
    path(
        'board/labels/beneficiaries/form/',
        labels_beneficiaries_form_view.LabelsBeneficiariesFormView.as_view(),
        name='labels_beneficiaries_form'
    ),

    path(
        'board/labels/beneficiaries/form/new/',
        labels_beneficiaries_form_view.LabelsBeneficiariesFormView.as_view(),
        name='labels_beneficiaries_form_new'
    ),

    path(
        'board/labels/beneficiaries/form/delete/type/',
        labels_beneficiaries_form_view.LabelsBeneficiariesFormView.as_view(),
        name='labels_beneficiaries_form_delete_type'
    ),

    # LABELS/CATEGORIES
    path(
        'board/labels/categories/',
        labels_categories_view.LabelsCategoriesView.as_view(),
        name='labels_categories'
    ),

    path(
        'board/labels/categories/edit/',
        labels_categories_view.LabelsCategoriesView.as_view(),
        name='labels_categories_edit'
    ),

    path(
        'board/labels/categories/delete/',
        labels_categories_view.LabelsCategoriesView.as_view(),
        name='labels_categories_delete'
    ),

    # LABELS/CATEGORIES/FORM
    path(
        'board/labels/categories/form/',
        labels_categories_form_view.LabelsCategoriesFormView.as_view(),
        name='labels_categories_form'
    ),

    path(
        'board/labels/categories/form/new/',
        labels_categories_form_view.LabelsCategoriesFormView.as_view(),
        name='labels_categories_form_new'
    ),

    path(
        'board/labels/categories/form/delete/category/',
        labels_categories_form_view.LabelsCategoriesFormView.as_view(),
        name='labels_categories_form_delete_category'
    ),

    # LABELS/CLIENTS
    path(
        'board/labels/clients/',
        labels_clients_view.LabelsClientsView.as_view(),
        name='labels_clients'
    ),

    path(
        'board/labels/clients/edit/',
        labels_clients_view.LabelsClientsView.as_view(),
        name='labels_clients_edit'
    ),

    path(
        'board/labels/clients/delete/',
        labels_clients_view.LabelsClientsView.as_view(),
        name='labels_clients_delete'
    ),

    # LABELS/CLIENTS/FORM
    path(
        'board/labels/clients/form/',
        labels_clients_form_view.LabelsClientsFormView.as_view(),
        name='labels_clients_form'
    ),

    path(
        'board/labels/clients/form/new/',
        labels_clients_form_view.LabelsClientsFormView.as_view(),
        name='labels_clients_form_new'
    ),

    # LABELS/FINANCIAL
    path(
        'board/labels/financial/',
        labels_financial_view.LabelsFinancialView.as_view(),
        name='labels_financial'
    ),

    path(
        'board/labels/financial/edit/',
        labels_financial_view.LabelsFinancialView.as_view(),
        name='labels_financial_edit'
    ),

    path(
        'board/labels/financial/delete/',
        labels_financial_view.LabelsFinancialView.as_view(),
        name='labels_financial_delete'
    ),

    # LABELS/FINANCIAL/FORM
    path(
        'board/labels/financial/form/',
        labels_financial_form_view.LabelsFinancialFormView.as_view(),
        name='labels_financial_form'
    ),

    path(
        'board/labels/financial/form/new/',
        labels_financial_form_view.LabelsFinancialFormView.as_view(),
        name='labels_financial_form_new'
    ),

    # PROFILE
    path(
        'board/profile/',
        profile_view.ProfileView.as_view(), name='profile'
    ),

    # PROFILE/PASSWORD/CHANGE
    path(
        'board/profile/password/change/',
        profile_password_view.ProfilePasswordView.as_view(), name='password'
    ),

    # 404
    path('board/404/', error_view.handler404, name='404'),

    # JS
    path('board/js/', js_ajax.JsView.as_view()),
    path('board/category/js/', js_ajax.JsView.as_view()),
    path('board/labels/beneficiaries/js/', js_ajax.JsView.as_view()),
    path('board/labels/categories/js/', js_ajax.JsView.as_view()),
    path('board/labels/categories/form/js/', js_ajax.JsView.as_view()),
    path('board/labels/clients/js/', js_ajax.JsView.as_view()),
    path('board/labels/clients/form/js/', js_ajax.JsView.as_view()),
    path('board/labels/financial/js/', js_ajax.JsView.as_view()),
]
