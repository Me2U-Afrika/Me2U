from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.HomeView.as_view(), name='blog_home',),
    path(r'post/<slug>/', views.PostDetailedView.as_view(), name='postView'),
    path(r'post-create/<pk>/', views.PostCreateView.as_view(), name='post_create'),
    path('like/<str:slug>', views.likeView, name='like_post'),
    path(r'post/<slug>/update', views.PostUpdateView.as_view(), name='post_update'),
    path(r'post/<slug>/delete', views.PostDeleteView.as_view(), name='post_delete'),

]
