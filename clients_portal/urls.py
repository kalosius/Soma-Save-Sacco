from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.startt, name='home'),

    path('client_dashboard', views.client_dashboard, name='client_dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register_view'),
    path('logout/', views.logout_view, name='logout'),
    path('userprofile/', views.userprofile, name='userprofile'),
    path('account/', views.user_account, name='account'),
    path('user_loans/', views.user_loans, name='user_loans'),
    path('client_shares/', views.shares, name='shares'),
    path('mystatement/', views.statement, name='statement'),
    path('loanrequest/', views.loanrequest, name='loanrequest'),
    path('withdrawal/', views.withdrawal, name='withdrawal'),
    path('transactions/', views.transactions, name='transactions'),

    # updating profile
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/upload-photo/', views.upload_photo, name='upload_photo'),


    # CVC and pdf
    path('mystatement/', views.statement, name='statement'),
    path('mystatement/download/<str:format>/', views.download_statement, name='download_statement'),




    # Password reset request form
    path('reset-password/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset_form.html'
    ), name='password_reset'),

    # Password reset done (email sent confirmation)
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),

   path('reset-password-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
    template_name='auth/password_reset_confirm.html',
    success_url='/client/reset-password-complete/'  # Note the leading slash!
), name='password_reset_confirm'),

    # Password reset complete (password changed successfully)
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),




# fluuterwave payment integration
    path("payment/momo/", views.momo_payment_form, name="momo_payment_form"),
    path("payment/initiate/", views.momo_payment_initiate, name="momo_payment_initiate"),
    path('payment/callback/', views.flutterwave_callback, name='flutterwave_callback'),


]