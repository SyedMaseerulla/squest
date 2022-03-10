from django.urls import resolve, Resolver404
from django.utils.deprecation import MiddlewareMixin


class ModelAdminMiddleware(MiddlewareMixin):

    def process_template_response(self, request, response):
        try:
            url = resolve(request.path_info)
        except Resolver404:
            return response
        if not url.app_name == 'admin' and url.url_name not in ['index', 'app_list']:
            # current view is not a django admin index
            # or app_list view, bail out!
            return response
        if 'available_apps' not in response.context_data:
            return response

        # print('ModelAdmin', response.context_data)
        ss_menu_models = []
        ss_survey_models = []
        ss_edb_models = []
        ss_so_models = []
        ss_sub_models = []
        ss_lca_models = []
        for i, app in enumerate(response.context_data['available_apps']):
            # print(app)
            if 'name' in app and app['name'] == 'Squest Survey':
                # print(app)
                for model in app['models']:
                    if model['name'] in ['Menu Items', 'Vendor Items']:
                        ss_menu_models.append(model)
                    if model['name'] in ['Templates', 'Categories', 'Questions', 'Calculations', 'Operations', 'Responses', 'Answers']:
                        ss_survey_models.append(model)
                    if model['name'] in ['EDB Templates', 'EDB Categories', 'EDB Questions']:
                        ss_edb_models.append(model)
                    if model['name'] in ['SO Templates', 'SO Categories', 'SO Questions']:
                        ss_so_models.append(model)
                    if model['name'] in ['Subscription Templates', 'Subscription Panels', 'Subscription Tabs', 'Subscription Configs']:
                        ss_sub_models.append(model)
                    if model['name'] in ['LCA Configs', 'LCA Operators']:
                        ss_lca_models.append(model)
                response.context_data['available_apps'].pop(i)
        # print(ss_survey_models)

        response.context_data['available_apps'].append({
            "name": "Squest Menu",
            "app_label": "squest_survey",
            "app_url": "/admin/squest_survey/",
            "has_module_perms": True,
            "models": ss_menu_models,
        })

        response.context_data['available_apps'].append({
            "name": "Squest Survey",
            "app_label": "squest_survey",
            "app_url": "/admin/squest_survey/",
            "has_module_perms": True,
            "models": ss_survey_models,
        })

        response.context_data['available_apps'].append({
            "name": "Squest Extend Database",
            "app_label": "squest_survey",
            "app_url": "/admin/squest_survey/",
            "has_module_perms": True,
            "models": ss_edb_models,
        })

        response.context_data['available_apps'].append({
            "name": "Squest Scale Out",
            "app_label": "squest_survey",
            "app_url": "/admin/squest_survey/",
            "has_module_perms": True,
            "models": ss_so_models,
        })

        response.context_data['available_apps'].append({
            "name": "Squest Subscription",
            "app_label": "squest_survey",
            "app_url": "/admin/squest_survey/",
            "has_module_perms": True,
            "models": ss_sub_models,
        })

        response.context_data['available_apps'].append({
            "name": "Squest LCA Configuration",
            "app_label": "squest_survey",
            "app_url": "/admin/squest_survey/",
            "has_module_perms": True,
            "models": ss_lca_models,
        })

        # print(f"{response.context_data['available_apps'] = }")
        # print(response.context_data['app_list'])
        return response
