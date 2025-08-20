from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_csv.renderers import CSVRenderer
from apps.payments.models import Payment
from apps.properties.models import Property
from .serializers import PaymentSerializer, PropertySerializer
import io
import csv

class PropertyImportExportViewSet(viewsets.ViewSet):
    """
    A viewset for importing and exporting property data.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PropertySerializer

    @action(detail=False, methods=['get'])
    def export_properties(self, request):
        """Export all properties to a CSV file."""
        properties = Property.objects.all()
        serializer = PropertySerializer(properties, many=True)
        renderer = CSVRenderer()
        csv_data = renderer.render(serializer.data)
        response = Response(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="properties.csv"'
        return response

    @action(detail=False, methods=['post'])
    def import_properties(self, request):
        """Import properties from a CSV file."""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'Please provide a file.'}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        serializer = self.serializer_class(data=list(reader), many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Properties imported successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentImportExportViewSet(viewsets.ViewSet):
    """
    A viewset for importing and exporting payment data.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    @action(detail=False, methods=['get'])
    def export_payments(self, request):
        """Export all payments to a CSV file."""
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        renderer = CSVRenderer()
        csv_data = renderer.render(serializer.data)
        response = Response(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payments.csv"'
        return response

    @action(detail=False, methods=['post'])
    def import_payments(self, request):
        """Import payments from a CSV file."""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'Please provide a file.'}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string)
        next(reader)  # Skip header row

        for row in reader:
            # Assuming CSV format: lease_id, amount, payment_date, due_date, payment_type, payment_method, status
            try:
                Payment.objects.create(
                    lease_id=row[0],
                    amount=row[1],
                    payment_date=row[2],
                    due_date=row[3],
                    payment_type=row[4],
                    payment_method=row[5],
                    status=row[6]
                )
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'Payments imported successfully.'})