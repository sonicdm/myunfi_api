from myunfi.config import api_base_url

"""
Homepage Endpoints
"""
home_root = api_base_url + "/api"
# USERS
users = home_root + "/users"
users_communication_preferences = users + "/communicationPreferences"
users_customers = users + "/customers"
users_details = users + "/details"
users_favorites = users + "/favorites"
users_favorites_application_links = users_favorites + "/applicationLinks"
users_profile = users + "/profile"

# ---AUTH---
auth = home_root + "/auth"
auth_validate = auth + "/validate"
# ---TOKENS---
tokens = home_root + "/tokens"
tokens_authorization_token = tokens + "/authorization-token"

home_user_endpoints = {
    "users": users,
    "users_communication_preferences": users_communication_preferences,
    "users_customers": users_customers,
    "users_details": users_details,
    "users_favorites": users_favorites,
    "users_favorites_application_links": users_favorites_application_links,
    "users_profile": users_profile,
}

# ---Users Application Categories---
# ?menuName=Tools
# ?menuName=Resources
# ?menuName=myTeamSites
# ?menuName=Featured%20Tools
users_application_categories = users + "/applicationCategories"
users_application_categories_menu_name = users_application_categories + "?menuName="
users_application_categories_menu_name_featured_tools = users_application_categories_menu_name + "Featured%20Tools"
users_application_categories_menu_name_my_team_sites = users_application_categories_menu_name + "myTeamSites"
users_application_categories_menu_name_resources = users_application_categories_menu_name + "Resources"
users_application_categories_menu_name_tools = users_application_categories_menu_name + "Tools"

# CONTENT
content = home_root + "/content"
# ---CONTENT - CUSTOMER---
content_customer = content + "/customer"
content_customer_news_center = content_customer + "/news-center"
content_customer_background_images = content_customer + "/background-images"
content_customer_landing_page = content_customer + "/landing-page"
content_customer_customer_care = content_customer + "/customer-care"
# CONTENT - ASSOCIATE
content_associate = content + "/associate"
content_associate_customer_care = content_associate + "/customer-care"
content_associate_services = content_associate + "/services"
content_associate_resources = content_associate + "/resources"

"""
Shopping Endpoints
&hostSystem=WBS is not needed
"""
shopping_root = api_base_url + "/shopping/api"

# AUTH
shopping_auth = shopping_root + "/auth"
shopping_auth_validate = shopping_auth + "/validate"

# CUSTOMERS
# https://www.myunfi.com/shopping/api/customers/001014/arrive/isEnabled?hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/brands/40579?hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/brands/grouped?numPerGroup=24&hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/brands?startsWith=A&hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/categories?parentId=76&hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/deliveryDepartments?hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/deliverySchedule?hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/departments?includeImages=false&hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/invoices/68646284-006?transactionType=INVOICE&hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/invoices?order=invoiceDate&page=0&size=12&sort=DESC&startInvoiceDate=2021-12-08&hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/invoices?order=invoiceDate&size=12&sort=DESC&startInvoiceDate=2021-12-08&hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/items/quantityOnHand?hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/items/recommended?page=0&size=12&hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/items/search?brands=40579&dcNumber=6&page=0&searchTerm=%2A&size=12&hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/items/search?dcNumber=6&page=0&searchTerm=searchterm&size=100&hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/items/top?size=12&hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/openOrders?hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/orderGuides?hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/orders?hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/orders?ordersFromDate=2021-12-09T00%3A00%3A00Z&hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/pricing?hostSystem=WBS
# https://www.myunfi.com/shopping/api/customers/001014/subcategories?parentId=1367&hostSystem=WBS
# Customers
shopping_customers = shopping_root + "/customers"
shopping_customers_account_id = shopping_customers + "/{accountID}"
## DELIVERY
shopping_customers_account_id_arrive = shopping_customers_account_id + "/arrive"
shopping_customers_account_id_arrive_is_enabled = shopping_customers_account_id_arrive + "/isEnabled"
shopping_customers_account_id_delivery_departments = shopping_customers_account_id + "/deliveryDepartments"
shopping_customers_account_id_delivery_schedule = shopping_customers_account_id + "/deliverySchedule"
shopping_customers_delivery_endpoints = {
    "arrive": shopping_customers_account_id_arrive,
    "arrive_is_enabled": shopping_customers_account_id_arrive_is_enabled,
    "delivery_departments": shopping_customers_account_id_delivery_departments,
    "delivery_schedule": shopping_customers_account_id_delivery_schedule
}
## BRANDS
shopping_customers_account_id_brands = shopping_customers_account_id + "/brands"
shopping_customers_account_id_brands_brand_id = shopping_customers_account_id_brands + "/{brandID}"
shopping_customers_account_id_brands_grouped = shopping_customers_account_id_brands + "/grouped?numPerGroup={numPerGroup}"
shopping_customers_brands_endpoints: dict[str, str] = {
    "grouped": shopping_customers_account_id_brands_grouped,
    "brand_id": shopping_customers_account_id_brands_brand_id,
    "base": shopping_customers_account_id_brands
}
## CATEGORIES
shopping_customers_account_id_categories = shopping_customers_account_id + "/categories?parentId={parentId}"
shopping_customers_account_id_subcategories = shopping_customers_account_id + "/subcategories?parentId={parentId}"
shopping_customers_categories_endpoints: dict[str, str] = {
    "categories": shopping_customers_account_id_categories,
    "subcategories": shopping_customers_account_id_subcategories
}
## DEPARTMENTS
shopping_customers_account_id_departments = shopping_customers_account_id + "/departments?includeImages={include_images}"
shopping_customers_departments_endpoints: dict[str, str] = {
    "departments": shopping_customers_account_id_departments
}
## ITEMS/SEARCH
shopping_customers_account_id_items = shopping_customers_account_id + "/items"
shopping_customers_account_id_items_quantity_on_hand = shopping_customers_account_id + "/items/quantityOnHand"
shopping_customers_account_id_items_recommended = shopping_customers_account_id_items + "/recommended"
shopping_customers_account_id_items_search = shopping_customers_account_id_items + "/search"
shopping_customers_account_id_items_top = shopping_customers_account_id_items + "/top?size={size}"
shopping_customers_account_id_pricing = shopping_customers_account_id + "/pricing"
shopping_customers_items_endpoints: dict[str, str] = {
    "items": shopping_customers_account_id_items,
    "quantity_on_hand": shopping_customers_account_id_items_quantity_on_hand,
    "recommended": shopping_customers_account_id_items_recommended,
    "search": shopping_customers_account_id_items_search,
    "top": shopping_customers_account_id_items_top,
    "pricing": shopping_customers_account_id_pricing
}

## ORDERS
shopping_customers_account_id_order_guides = shopping_customers_account_id + "/orderGuides"
shopping_customers_account_id_orders = shopping_customers_account_id + "/orders"
shopping_customers_account_id_open_orders = shopping_customers_account_id + "/openOrders"
shopping_customers_account_id_open_orders_order_number = shopping_customers_account_id_orders + "/{orderNumber}"
shopping_customers_account_id_invoices = shopping_customers_account_id + "/invoices"
shopping_customers_account_id_invoices_invoice_id = shopping_customers_account_id_invoices + "/{invoiceID}"
shopping_customers_account_id_orders_open_orders = shopping_customers_account_id_orders + "/openOrders"
shopping_customers_account_id_orders_order_id = shopping_customers_account_id_orders + "/{orderID}"
shopping_customers_account_id_orders_order_id_items = shopping_customers_account_id_open_orders_order_number + "/items"
shopping_customers_orders_endpoints: dict[str, str] = {
    "order_guides": shopping_customers_account_id_order_guides,
    "orders": shopping_customers_account_id_orders,
    "invoices": shopping_customers_account_id_invoices,
    "invoice_id": shopping_customers_account_id_invoices_invoice_id,
    "open_orders": shopping_customers_account_id_orders_open_orders,
    "order_id": shopping_customers_account_id_orders_order_id
}

# USERS
# https://www.myunfi.com/shopping/api/users/application-information?hostSystem=WBS
# https://www.myunfi.com/shopping/api/users/applicationCategories?menuName=Tools&hostSystem=WBS
# https://www.myunfi.com/shopping/api/users/applicationCategories?menuName=Resources&hostSystem=WBS
# https://www.myunfi.com/shopping/api/users/applications?appNames=WebOrdering,MobileOrdering,WebOrderingAdmin
# https://www.myunfi.com/shopping/api/users/details?hostSystem=WBS
shopping_users = shopping_root + "/users"
shopping_users_application_categories = shopping_users + "/applicationCategories"
shopping_users_application_categories_menu_name = shopping_users_application_categories + "?menuName="
shopping_users_application_categories_resources = shopping_users_application_categories_menu_name + "Resources"
shopping_users_application_categories_tools = shopping_users_application_categories_menu_name + "Tools"
shopping_users_application_information = shopping_users + "/application-information"
shopping_users_applications = shopping_users + "/applications?appNames={app_names}"
shopping_users_details = shopping_users + "/details"
shopping_users_endpoints = {
    "application_categories": shopping_users_application_categories,
    "application_categories_menu_name": shopping_users_application_categories_menu_name,
    "application_categories_resources": shopping_users_application_categories_resources,
    "application_categories_tools": shopping_users_application_categories_tools,
    "application_information": shopping_users_application_information,
    "applications": shopping_users_applications,
    "details": shopping_users_details
}

# CONTENT
# https://www.myunfi.com/shopping/api/content/brands/logos?hostSystem=WBS
# https://www.myunfi.com/shopping/api/content/publications?chainCode=CAP&customerSegmentCode=NATIND&dcNumber=6&hostSystem=WBS&isHonestGreen=false&hostSystem=WBS
shopping_content = shopping_root + "/content"
shopping_content_brands = shopping_content + "/brands"
shopping_content_brands_logos = shopping_content_brands + "/logos"
shopping_content_publications = shopping_content + "/publications"
shopping_content_endpoints = {
    "brands": shopping_content_brands,
    "brands_logos": shopping_content_brands_logos,
    "publications": shopping_content_publications
}
