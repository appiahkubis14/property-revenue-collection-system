from django.urls import path
from core.main import *
from django.contrib.auth import views as auth_views
from core.views.property_registry.registry import *
from core.views.property_registry.valuation import *
from core.views.property_registry.classification import *
from core.views.property_registry.owner import *
from core.views.property_registry.map import *
from core.views.billing.bill_generation import *
from core.views.billing.rate_management import *
from core.views.billing.tax_calculation import *
from core.views.billing.billing_cycles import *
from core.views.map.map import *



urlpatterns = [
    path('dashboard/', index, name='dashboard'),
    path('welcome/', dashboard_view, name='welcome'),
    path('', landing, name='landing'),
    path('login/', auth_views.LoginView.as_view(template_name="auth/auth-login.html"), name='login'),
    path('logout/', custom_logout, name='logout'),  # Use custom logout view
    path('change-password/', change_password, name='change_password'),

    path('property-registry/', property_registry, name='property-registry'),
    path('api/properties/', get_properties, name='get-properties'),
    path('api/properties/add/', add_property, name='add-property'),
    path('api/properties/<int:property_id>/', get_property_detail, name='get-property-detail'),
    path('api/properties/<int:property_id>/update/', update_property, name='update-property'),
    path('api/properties/<int:property_id>/delete/', delete_property, name='delete-property'),

    path('property-valuation/', property_valuation, name='property-valuation'),
    path('api/valuations/', get_valuations, name='get-valuations'),
    path('api/valuations/add/', create_valuation, name='create-valuation'),
    path('api/valuations/<int:bill_id>/', get_valuation_detail, name='get-valuation-detail'),
    path('api/valuations/<int:bill_id>/update/', update_valuation, name='update-valuation'),
    path('api/valuations/<int:bill_id>/delete/', delete_valuation, name='delete-valuation'),
    path('api/properties/<int:property_id>/details/', get_property_details, name='get-property-details'),

    path('property-classification/', property_classification, name='property-classification'),
    path('api/classifications/', get_classifications, name='get-classifications'),
    path('api/classifications/<int:property_id>/update/', update_classification, name='update-classification'),
    path('api/classifications/<int:property_id>/analysis/', get_classification_analysis, name='get-classification-analysis'),
    path('api/classifications/stats/', get_classification_stats, name='get-classification-stats'),

    path('property-owners/', owner_management, name='owner-management'),
    path('api/owners/', get_owners, name='get-owners'),
    path('api/owners/add/', add_owner, name='add-owner'),
    path('api/owners/<int:owner_id>/', get_owner_detail, name='get-owner-detail'),
    path('api/owners/<int:owner_id>/update/', update_owner, name='update-owner'),
    path('api/owners/<int:owner_id>/delete/', delete_owner, name='delete-owner'),
    path('api/owners/stats/', get_owner_stats, name='get-owner-stats'),
    path('api/owners/search/', search_owners, name='search-owners'),
    path('api/properties/<int:property_id>/owners/', get_property_owners, name='get-property-owners'),

    path('bill-generation/', bill_generation_page, name='bill_generation'),
    path('api/bills/', get_bills, name='get_bills'),
    path('api/bills/generate/', generate_bill, name='generate_bill'),
    path('api/bills/bulk-generate/', bulk_generate_bills, name='bulk_generate_bills'),
    path('api/bills/<int:bill_id>/', get_bill_details, name='get_bill_details'),
    path('api/bills/<int:bill_id>/update/', update_bill, name='update_bill'),
    path('api/bills/<int:bill_id>/delete/', delete_bill, name='delete_bill'),
    path('api/properties/billing/', get_properties_for_billing, name='get_properties_for_billing'),
    path('api/billing-cycles/', get_billing_cycles, name='get_billing_cycles'),
    path('api/calculate-tax/', calculate_tax_amount, name='calculate_tax'),

    path('billing/rates-management/', rate_management_page, name='rate_management'),
    path('api/tax-rates/', get_tax_rates, name='get_tax_rates'),
    path('api/tax-rates/create/', create_tax_rate, name='create_tax_rate'),
    path('api/tax-rates/<int:rate_id>/update/', update_tax_rate, name='update_tax_rate'),
    path('api/tax-rates/<int:rate_id>/delete/', delete_tax_rate, name='delete_tax_rate'),
    path('api/zones-property-types/', get_zones_and_property_types, name='get_zones_property_types'),
    path('api/tax-rates/history/<int:zone_id>/<int:property_type_id>/', get_tax_rate_history, name='get_tax_rate_history'),
    path('api/tax-rates/current-report/', get_current_rates_report, name='get_current_rates_report'),
    path('api/tax-rates/bulk-update/', bulk_update_rates, name='bulk_update_rates'),


     path('billing/tax-calculation/', tax_calculation_page, name='tax_calculation'),
    path('api/tax/calculate/', calculate_tax_for_property, name='calculate_tax'),
    path('api/tax/bulk-calculate/', bulk_tax_calculation, name='bulk_tax_calculation'),
    path('api/tax/recent-calculations/', get_recent_calculations, name='recent_calculations'),
    path('api/tax/history/<int:property_id>/', get_tax_calculation_history, name='get_tax_history'),
    path('api/tax/simulate/', simulate_tax_scenario, name='simulate_tax_scenario'),
    path('api/tax/summary-report/', get_tax_summary_report, name='get_tax_summary'),
    path('api/tax/save-draft/', save_calculation_as_draft, name='save_calculation_draft'),


    # Billing Cycles URLs
    path('billing-cycles/', billing_cycles_page, name='billing_cycles'),
    path('api/billing-cycles/', get_billing_cycles_list, name='get_billing_cycles_list'),
    path('api/billing-cycles/create/', create_billing_cycle, name='create_billing_cycle'),
    path('api/billing-cycles/<int:cycle_id>/update/', update_billing_cycle, name='update_billing_cycle'),
    path('api/billing-cycles/<int:cycle_id>/delete/', delete_billing_cycle, name='delete_billing_cycle'),
    path('api/billing-cycles/<int:cycle_id>/', get_billing_cycle_details, name='get_billing_cycle_details'),
    path('api/billing-cycles/upcoming/', get_upcoming_cycles, name='get_upcoming_cycles'),
    path('api/billing-cycles/generate-batch/', generate_cycles_batch, name='generate_cycles_batch'),
    path('api/billing-cycles/performance/', get_cycle_performance, name='get_cycle_performance'),

    path('properties/mapping/', property_mapping, name='property_mapping'),
    path('api/properties/geojson/', get_properties_geojson, name='get_properties_geojson'),
    path('api/zones/geojson/', get_zones_geojson, name='get_zones_geojson'),
    path('api/districts/geojson/', get_districts_geojson, name='get_districts_geojson'),
    # path('api/map/analytics/', get_map_analytics, name='get_map_analytics'),
    path('api/property/<str:property_id>/', get_property_details, name='get_property_details'),
    path('api/search/properties/', search_properties, name='search_properties'),


    path('api/map/properties/', properties_list, name='properties_list'),
    path('api/map/properties/<str:identifier>/', property_detail, name='property_detail'),
    path('api/map/zones/', zones_list, name='zones_list'),
    path('api/map/zones/performance/', zones_performance, name='zones_performance'),
    path('api/map/districts/', districts_list, name='districts_list'),
    path('api/map/search/', search_properties, name='search_properties'),
    path('api/map/heatmap/', heatmap_data, name='heatmap_data'),
]