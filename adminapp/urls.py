from django.urls import path
from . import views

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BorrowerViewSet, LoanViewSet, PaymentViewSet, ReportViewSet, RepaymentScheduleViewSet

router = DefaultRouter()
router.register(r'borrowers', BorrowerViewSet)
router.register(r'loans', LoanViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'reports', ReportViewSet)
router.register(r'schedules', RepaymentScheduleViewSet)



urlpatterns = [
    # api
    path('api/admin', include(router.urls)),




    path('', views.dashboard, name='dashboard'),
    path('add_borrower/', views.add_borrower, name='add_borrower'),
    path('add_payment/', views.add_payment, name='add_payment'),
    path('add_loan/', views.add_loan, name='add_loan'),
    path('loans/', views.loans, name='loans'),
    path('borrowers/', views.borrowers, name='borrowers'),
    path('payments/', views.payments, name='payments'),
    path('reports/', views.reports, name='reports'),

    # no APIs available soffer
    path('users/', views.admin_users_list, name='admin_users_list'),
    path('admin/share-transactions/', views.admin_sharetransactions_list, name='admin_sharetransactions_list'),
    path('admin/deposits/', views.admin_deposits_list, name='admin_deposits_list'),
    path('admin/accounts/', views.admin_accounts_list, name='admin_accounts_list'),
    path('admin/login-activities/', views.admin_loginactivities_list, name='admin_loginactivities_list'),
    # no APIs available soffer



    # editing and deleting
    path('borrower/edit/<int:id>/', views.edit_borrower, name='edit_borrower'),
    path('borrower/delete/<int:id>/', views.delete_borrower, name='delete_borrower'),
    path('loan/edit/<int:id>/', views.edit_loan, name='edit_loan'),
    path('loan/delete/<int:id>/', views.delete_loan, name='delete_loan'),

    # adminforms
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('not-authorized/', views.not_authorized, name='not_authorized'),

]
