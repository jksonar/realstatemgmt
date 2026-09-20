import factory
from factory.django import DjangoModelFactory
from .models import Property, Tenant, Lease, Payment, MaintenanceRequest, CustomUser

class UserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class PropertyFactory(DjangoModelFactory):
    class Meta:
        model = Property

    property_id = factory.Sequence(lambda n: f'P{n:03}')
    address = factory.Faker('address')
    city = factory.Faker('city')
    area = factory.Faker('street_name')
    property_type = '2BHK'
    size_sqft = 1200
    rent_amount = 1500.00
    deposit_amount = 3000.00
    status = 'available'
    furnished_type = 'fully-furnished'

class TenantFactory(DjangoModelFactory):
    class Meta:
        model = Tenant

    tenant_id = factory.Sequence(lambda n: f'T{n:03}')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    address = factory.Faker('address')
    id_proof_type = 'Passport'
    id_proof_number = factory.Sequence(lambda n: f'A{n:07}')

class LeaseFactory(DjangoModelFactory):
    class Meta:
        model = Lease

    lease_id = factory.Sequence(lambda n: f'L{n:03}')
    property = factory.SubFactory(PropertyFactory)
    tenant = factory.SubFactory(TenantFactory)
    start_date = factory.Faker('date_this_year')
    end_date = factory.Faker('date_this_year')
    monthly_rent = 1500.00
    security_deposit = 3000.00
    status = 'active'

class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    payment_id = factory.Sequence(lambda n: f'PAY{n:04}')
    lease = factory.SubFactory(LeaseFactory)
    amount = 1500.00
    payment_date = factory.Faker('date_this_month')
    due_date = factory.Faker('date_this_month')
    payment_type = 'rent'
    payment_method = 'card'
    status = 'paid'

class MaintenanceRequestFactory(DjangoModelFactory):
    class Meta:
        model = MaintenanceRequest

    request_id = factory.Sequence(lambda n: f'MR{n:04}')
    property = factory.SubFactory(PropertyFactory)
    tenant = factory.SubFactory(TenantFactory)
    issue_type = 'Plumbing'
    description = factory.Faker('text')
    priority = 'medium'
    status = 'reported'
