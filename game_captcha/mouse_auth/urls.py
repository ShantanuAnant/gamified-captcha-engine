from django.urls import path
from .views import (
    CollectTrainingDataView,
    TrainModelView,
    VerifyUserIdentityView
)

urlpatterns = [
    path('/collect-data/', CollectTrainingDataView.as_view(), name='collect-mouse-data'),
    path('/train-model/', TrainModelView.as_view(), name='train-mouse-model'),
    path('/verify-user/', VerifyUserIdentityView.as_view(), name='verify-user-mouse'),
]