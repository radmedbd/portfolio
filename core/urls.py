from django.urls import path
from . import views

urlpatterns = [
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("cv/", views.cv, name="cv"),
    path("experience/", views.experience, name="experience"),
    path("research/", views.research_list, name="research_list"),
    path("research/<slug:slug>/", views.research_detail, name="research_detail"),
    path("projects/", views.projects, name="projects"),
    path("research-hub/", views.hub_list, name="hub_list"),
    path("research-hub/<slug:slug>/", views.hub_detail, name="hub_detail"),
    path("people/", views.people_list, name="people_list"),
    path("people/<slug:slug>/", views.people_detail, name="people_detail"),
    path("contact/", views.contact, name="contact"),
    path("contact/success/", views.contact_success, name="contact_success"),
    path("search/", views.search, name="search"),
]
