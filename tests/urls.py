from django.urls import include, path

from landelayo.urls import router

urlpatterns = [
    path('landelayo/', include(router.urls)),
]