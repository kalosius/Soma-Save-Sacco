from django.urls import path
from . import views

urlpatterns = [
   path('', views.dashboard, name='dashboard'),
    path('add_borrower/', views.add_borrower, name='add_borrower'),
    path('add_payment/', views.add_payment, name='add_payment'),
    path('add_loan/', views.add_loan, name='add_loan'),
    path('loans/', views.loans, name='loans'),
    path('borrowers/', views.borrowers, name='borrowers'),
    path('payments/', views.payments, name='payments'),
    path('reports/', views.reports, name='reports'),
]
