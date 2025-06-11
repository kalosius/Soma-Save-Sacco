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

    # editing and deleting
    path('borrower/edit/<int:id>/', views.edit_borrower, name='edit_borrower'),
    path('borrower/delete/<int:id>/', views.delete_borrower, name='delete_borrower'),
    path('loan/edit/<int:id>/', views.edit_loan, name='edit_loan'),
    path('loan/delete/<int:id>/', views.delete_loan, name='delete_loan'),
]
