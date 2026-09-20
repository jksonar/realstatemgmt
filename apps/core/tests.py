from django.test import TestCase
from .models import Property, Tenant, Lease, Payment, MaintenanceRequest
from .factories import PropertyFactory, TenantFactory, LeaseFactory, PaymentFactory, MaintenanceRequestFactory

class PropertyModelTest(TestCase):
    def test_property_creation(self):
        property = PropertyFactory()
        self.assertIsInstance(property, Property)
        self.assertEqual(str(property), property.property_id)

class TenantModelTest(TestCase):
    def test_tenant_creation(self):
        tenant = TenantFactory()
        self.assertIsInstance(tenant, Tenant)
        self.assertEqual(str(tenant), tenant.tenant_id)

class LeaseModelTest(TestCase):
    def test_lease_creation(self):
        lease = LeaseFactory()
        self.assertIsInstance(lease, Lease)
        self.assertEqual(str(lease), lease.lease_id)

class PaymentModelTest(TestCase):
    def test_payment_creation(self):
        payment = PaymentFactory()
        self.assertIsInstance(payment, Payment)
        self.assertEqual(str(payment), payment.payment_id)

class MaintenanceRequestModelTest(TestCase):
    def test_maintenance_request_creation(self):
        maintenance_request = MaintenanceRequestFactory()
        self.assertIsInstance(maintenance_request, MaintenanceRequest)
        self.assertEqual(str(maintenance_request), maintenance_request.request_id)
