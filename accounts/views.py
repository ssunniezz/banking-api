from decimal import Decimal

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from .models import Account, Transaction, User
from .serializers import AccountSerializer, TransactionSerializer, UserSerializer

# Custom views for deposit, withdraw, transfer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status, generics, permissions


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class UserTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class UserTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'account_id', openapi.IN_QUERY, description="ID of the account to filter transactions",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'to_account_id', openapi.IN_QUERY, description="ID of the to_account to filter transactions",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'transaction_type', openapi.IN_QUERY,
                description="Type of the transaction to filter (deposit, withdraw, transfer)", type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = super().get_queryset()
        account_id = self.request.query_params.get('account_id')
        to_account_id = self.request.query_params.get('to_account_id')
        transaction_type = self.request.query_params.get('transaction_type')

        if account_id:
            queryset = queryset.filter(account_id=account_id)
        if to_account_id:
            queryset = queryset.filter(to_account_id=to_account_id)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)

        return queryset


class CustomAccountViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        operation_description="Deposit an amount into a specific bank account.",
        request_body=openapi.Schema(
            title='Body',
            type=openapi.TYPE_OBJECT,
            properties={
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount to deposit')
            },
            required=['amount']
        ),
        responses={200: 'Deposit successful'}
    )
    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        # Update account
        account = Account.objects.get(pk=pk)
        amount = request.data.get('amount')
        account.balance += Decimal(amount)
        account.save()

        # Save transaction
        Transaction.objects.create(
            account=account,
            amount=amount,
            transaction_type='deposit'
        )

        return Response({'status': 'deposit successful'})

    @swagger_auto_schema(
        operation_description="Withdraw an amount from a specific bank account.",
        request_body=openapi.Schema(
            title='Body',
            type=openapi.TYPE_OBJECT,
            properties={
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount to withdraw')
            },
            required=['amount']
        ),
        responses={200: 'Withdraw successful', 400: 'Insufficient funds'}
    )
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        account = Account.objects.get(pk=pk)
        amount = request.data.get('amount')
        if account.balance >= Decimal(amount):
            # Update account
            account.balance -= Decimal(amount)
            account.save()

            # Save transaction
            Transaction.objects.create(
                account=account,
                amount=amount,
                transaction_type='withdraw'
            )

            return Response({'status': 'withdraw successful'})
        return Response({'status': 'insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Transfer an amount from one bank account to another.",
        request_body=openapi.Schema(
            title='Body',
            type=openapi.TYPE_OBJECT,
            properties={
                'to_account_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                description='ID of the account to transfer to'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount to transfer')
            },
            required=['to_account_id', 'amount']
        ),
        responses={200: 'Transfer successful', 400: 'Insufficient funds / Cannot transfer to the same account'}
    )
    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        from_account = Account.objects.get(pk=pk)
        to_account_id = request.data.get('to_account_id')
        amount = request.data.get('amount')
        to_account = Account.objects.get(id=to_account_id)

        if from_account.id == to_account.id:
            return Response({'status': 'cannot transfer to the same account'}, status=status.HTTP_400_BAD_REQUEST)

        if from_account.balance >= Decimal(amount):
            # Update accounts
            from_account.balance -= Decimal(amount)
            to_account.balance += Decimal(amount)
            from_account.save()
            to_account.save()

            # Save transaction
            Transaction.objects.create(
                account=from_account,
                to_account=to_account,
                amount=amount,
                transaction_type='transfer'
            )

            return Response({'status': 'transfer successful'})
        return Response({'status': 'insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
