"""
API for the contracts application.

This module contains the API for the contracts application.
"""
from datetime import datetime
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action, permission_classes

from contracts.models import ContractType, Contract, Country, Currency, Personeltype, \
    Personel, Addendum
from .serializers import ContractTypeSerializer, ContractSerializer, \
    CountrySerializer, CurrencySerializer, PersonelTypeSerializer, PersonelSerializer, \
    ContractAddendumSerializer
from contracts.services import ContractService

# pylint: disable=too-many-ancestors
class ContractTypeAPI(viewsets.ModelViewSet):
    """
    API for the ContractType model.
    """
    queryset = ContractType.objects.order_by('contracttypeid')

    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ContractTypeSerializer


class ContractAPI(viewsets.ModelViewSet):
    """
    API for the Contract model.
    """
    queryset = Contract.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = ContractSerializer


class ContractAPIEx(APIView):
    """
    API for the Contract model.
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    # READ ContractS
    def get(self, request, userid):
        """
        Get the contracts for a user.
        """
        data = ContractService().read_contract(userid)
        return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)


class CountryAPI(viewsets.ModelViewSet):
    """
    API for the Country model.
    """
    queryset = Country.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = CountrySerializer


class CurrencyAPI(viewsets.ModelViewSet):
    """
    API for the Currency model.
    """
    queryset = Currency.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = CurrencySerializer


class PersonelTypeAPI(viewsets.ModelViewSet):
    """
    API for the PersonelType model.
    """
    queryset = Personeltype.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = PersonelTypeSerializer


class PersonelAPI(viewsets.ModelViewSet):
    """
    API for the Personel model.
    """
    queryset = Personel.objects.all()

    permission_classes = [
        permissions.IsAuthenticated
    ]

    serializer_class = PersonelSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_contract_base_info(request, contract_id, date_id):
    """
    Get the contract base info for a contract.
    """
    data, projectManagerConfirmed = ContractService().read_contract_base_info(contract_id, date_id)
    return Response(
            {
                "status": "success",
                "contractInfo": data,
                "projectManagerConfirmed": projectManagerConfirmed
            },
            status=status.HTTP_200_OK
        )


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def put_start_operation_date(request, contract_id, date):
    """
    Update the start operation date for a contract.
    """
    ContractService().update_start_operation_date(contract_id, date)
    return Response({"status": "success"}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def put_notification_date(request, contract_id, date):
    """
    Update the notification date for a contract.
    """
    ContractService().update_notification_date(contract_id, date)
    return Response({"status": "success"}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def put_plan_start_date(request, contract_id, date):
    """
    Update the plan start date for a contract.
    """
    ContractService().update_plan_start_date(contract_id, date)
    return Response({"status": "success"}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def put_finish_date(request, contract_id, date):
    """
    Update the finish date for a contract.
    """
    ContractService().update_finish_date(contract_id, date)
    return Response({"status": "success"}, status=status.HTTP_200_OK)


class ContractInfoAPI(APIView):
    """API for contract detailed information."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, contract_id):
        """Get contract consultant and EPC corporation info."""
        # You can determine what to return based on query params
        info_type = request.query_params.get('type', 'consultant')
        
        if info_type == 'consultant':
            data = ContractService.read_contract_consultan(contract_id)
        elif info_type == 'epc':
            data = ContractService.read_epc_corporation(contract_id)
        else:
            data = None

        return Response({
            "status": "success",
            "data": data
        }, status=status.HTTP_200_OK)

    def patch(self, request, contract_id):
        """Update the contract base info."""
        updated_data = ContractService.update_contract_base_info(contract_id, request.data)
        return Response({
            "status": "success",
            "data": updated_data
        }, status=status.HTTP_200_OK)


# Alternative: Separate views for consultant and EPC
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_contract_consultant(request, contract_id):
    """Get the contract consultant for a contract."""
    data = ContractService.get_contract_consultant(contract_id)
    return Response({
        "status": "success",
        "data": data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_epc_corporation(request, contract_id):
    """Get the EPC corporation for a contract."""
    data = ContractService.get_epc_corporation(contract_id)
    return Response({
        "status": "success",
        "data": data
    }, status=status.HTTP_200_OK)


# pylint: disable=too-many-ancestors
class ContractAddendumAPI(viewsets.ModelViewSet):
    """
    API for the ContractAddendum model.
    """
    queryset = Addendum.objects.all()

    serializer_class = ContractAddendumSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['get'])
    def contract_addendum_list(self, request, contract_id):
        """
        Get the contract addendum list for a contract.
        """
        data = ContractService().read_contract_addendum_list(request, contract_id)
        return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)
