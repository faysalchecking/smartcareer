from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceCatalogViewSet, VendorViewSet, PurchaseViewSet,
    SaleViewSet, InvoiceViewSet, PaymentViewSet, ExpenseViewSet,
    CommissionViewSet, TaxConfigViewSet, LedgerViewSet, BankAccountViewSet
)

router = DefaultRouter()
router.register(r'services', ServiceCatalogViewSet, basename='service')
router.register(r'vendors', VendorViewSet, basename='vendor')
router.register(r'purchases', PurchaseViewSet, basename='purchase')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'commissions', CommissionViewSet, basename='commission')
router.register(r'taxes', TaxConfigViewSet, basename='tax')
router.register(r'ledger', LedgerViewSet, basename='ledger')
router.register(r'accounts', BankAccountViewSet, basename='account')

urlpatterns = [
    path('', include(router.urls)),
]