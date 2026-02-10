from django.urls import path
from .views import token_login, upload_csv, summary, history, report_pdf

urlpatterns = [
    path('auth/token/', token_login, name='token_login'),
    path('upload/', upload_csv, name='upload_csv'),
    path('summary/', summary, name='summary'),
    path('history/', history, name='history'),
    path('report/pdf/', report_pdf, name='report_pdf'),
]
