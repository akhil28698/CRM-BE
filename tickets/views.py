from rest_framework import generics, permissions, exceptions
from .models import Ticket
from .serializers import TicketListSerializer, TicketSerializer

from users.models import User


class TicketListView(generics.ListAPIView):
    serializer_class = TicketListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Ticket.objects.all()

        if user.role == User.ROLE_ADMIN:
            # Get query parameters
            employee_id = self.request.query_params.get("employee_id", None)
            customer_id = self.request.query_params.get("customer_id", None)

            if employee_id:
                queryset = queryset.filter(assigned_id=employee_id)
            if customer_id:
                queryset = queryset.filter(created_by_id=customer_id)

        elif user.role == User.ROLE_EMPLOYEE:
            queryset = queryset.filter(assigned=user)

        elif user.role == User.ROLE_CUSTOMER:
            queryset = queryset.filter(created_by=user)

        return queryset


class TicketCreateView(generics.CreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == "customer" and self.request.data.get("assigned") is not None:
            raise exceptions.ValidationError(
                {"assigned": "Customers are not allowed to assign tickets."}
            )

        serializer.save(created_by=user)
