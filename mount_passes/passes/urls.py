from django.urls import path
from .views import SubmitDataView, get_pass_by_id, update_pass_status

urlpatterns = [
    path('submitData/', SubmitDataView.as_view(), name='submit-data'),
    path('submitData/<int:pk>/', get_pass_by_id, name='get-pass-by-id'),
    path('submitData/<int:pk>/status/', update_pass_status, name='update-pass-status'),
]