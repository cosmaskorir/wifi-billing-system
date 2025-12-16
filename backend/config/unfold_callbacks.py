# backend/config/unfold_callbacks.py

from collections import defaultdict
from django.conf import settings
from django.contrib import admin 

# Define the logical groupings here based on the exact plural names visible in the Admin
# We use multiple possible names for robustness.
GROUPS = {
    # 💰 BILLING - Should include Subscriptions, Payments, and maybe Data Usage models
    "BILLING": ["Payments", "Subscriptions"],
    
    # 🎫 SUPPORT - Should include Tickets and Ticket Updates
    "SUPPORT": ["Tickets", "Ticket Updates"], 
    
    # 📡 NETWORK - Consolidate Plans and Routers here
    "NETWORK": ["WiFi Packages", "Routers"], 
    
    # 🔑 AUTHENTICATION AND AUTHORIZATION - Covers Users, Groups, and Password Reset Tokens
    # Note: 'User' and 'Group' are often grouped under 'Authentication and Authorization'
    "AUTHENTICATION_AND_AUTHORIZATION": ["Users", "Groups", "Password Reset Tokens", "User"], 
}

def custom_dashboard_callback(request, context):
    """
    Groups models into logical sections for the Unfold sidebar and dashboard.
    """
    admin_site = admin.site
    
    # 1. Get the populated list of apps/models from the core admin site
    app_list = admin_site.get_app_list(request)
    
    grouped_apps = defaultdict(list)
    
    for app in app_list:
        for model in app["models"]:
            group_key = None
            # Use the model's display name
            model_name = model["name"]
            
            # 2. Check against custom GROUPS defined above
            for key, models_list in GROUPS.items():
                if model_name in models_list:
                    group_key = key
                    break
            
            # 3. Handle models that are not explicitly grouped but belong to a specific app
            if group_key is None:
                app_label = app["app_label"].upper()
                if app_label == 'USERS' or app_label == 'AUTH':
                    group_key = 'AUTHENTICATION_AND_AUTHORIZATION'
                elif app_label == 'PLANS' or app_label == 'ROUTERS':
                    group_key = 'NETWORK'
                # Default fallback: use the app name itself
                else:
                    group_key = app_label 

            grouped_apps[group_key].append(model)
    
    # 4. Reformat and Order the list using the structure defined in settings.py
    ordered_apps = []
    defined_ordering = settings.UNFOLD["EXTENSIONS"]["model_admin"]["ordering"]
    
    for group_name in defined_ordering:
        if group_name in grouped_apps:
            # Create the dictionary for the ordered list
            ordered_apps.append({
                "name": group_name.replace('_', ' ').title(), 
                "app_label": group_name.lower(),
                "models": grouped_apps[group_name],
            })
            del grouped_apps[group_name]
            
    # Add any remaining (ungrouped) apps at the end
    for group_name, models in grouped_apps.items():
        ordered_apps.append({
            "name": group_name.replace('_', ' ').title(),
            "app_label": group_name.lower(),
            "models": models,
        })
            
    context["apps"] = ordered_apps
    return context