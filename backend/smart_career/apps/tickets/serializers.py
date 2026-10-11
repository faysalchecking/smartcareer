from rest_framework import serializers
from smart_career.apps.medical.models import Ticket, Deployment

class TicketSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_id', 'candidate_name', 'pnr', 'ticket_number',
            'airline', 'flight_number', 'departure_airport', 'arrival_airport',
            'departure_date', 'departure_time', 'arrival_date', 'arrival_time',
            'ticket_cost', 'ticket_sale_price', 'currency', 'status', 'created_at'
        ]

class DeploymentSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    employer_name = serializers.CharField(source='employer.company_name', read_only=True)
    
    class Meta:
        model = Deployment
        fields = [
            'id', 'deployment_id', 'candidate_name', 'employer_name', 'job',
            'deployment_date', 'arrival_date', 'onboarding_date', 'status',
            'position', 'salary', 'currency', 'contract_start_date', 'contract_end_date',
            'contact_person', 'contact_phone', 'accommodation_address', 'remarks'
        ]