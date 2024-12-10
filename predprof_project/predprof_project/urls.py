from django.urls import include, path

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('', include('notes_to_music.urls')),
]