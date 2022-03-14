from ..endpoints import home_user_endpoints


"""
home_user_endpoints = {
    "users": users,
    "users_communication_preferences": users_communication_preferences,
    "users_customers": users_customers,
    "users_details": users_details,
    "users_favorites": users_favorites,
    "users_favorites_application_links": users_favorites_application_links,
    "users_profile": users_profile,
}
"""

def fetch_user_profile_checked(session, user_id) -> bool:
    """
    Fetch user profile
    GET
    https://www.myunfi.com/api/users/profile
    accept: application/json, text/plain, */*
    """
    endpoint = home_user_endpoints["users_profile"]
    response = session.get(endpoint)
    response.raise_for_status()
    json_response = JSONResponse(response)
    return session.get(home_user_endpoints.get_user_profile(user_id))