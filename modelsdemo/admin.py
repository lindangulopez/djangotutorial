from django.apps import apps
from django.contrib import admin

# Register every model in the demo app, including the proxies, so each can be
# browsed in the admin. Abstract models have no table and aren't listed.
for model in apps.get_app_config("modelsdemo").get_models():
    admin.site.register(model)
