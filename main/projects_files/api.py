"""
API views for the projects_files application.
All business logic has been moved to services.py.
"""
from django.http import FileResponse
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser

from projects_files.models import (
    HseReportDox, ProjectDox, ContractorDox, ProjectMonthlyDox,
    InvoiceDox, ReportDox, Zone, ZoneImage, ReportVisit
)
from projects_files.serializers import (
    HseReportDoxSerializers, ProjectDoxSerializers, ContractorDoxSerializers,
    ProjectMonthlyDoxSerializers, ApprovedInvoiceDoxSerializers, ReportDoxSerializers,
    ZoneSerializers, ZoneImagesSerializers, ProjectZoneImagesSerializers,
    ReportVisitSerializers
)
from projects_files.services import (
    FileDownloadService, HseReportDoxService, ProjectDoxService,
    ContractorDoxService, ProjectMonthlyDoxService, ApprovedInvoiceDoxService,
    ReportDoxService, ZoneService, ZoneImageService, ReportVisitService
)


class HseReportDoxAPI(viewsets.ModelViewSet):
    """API for the HseReportDox model."""
    
    queryset = HseReportDox.objects.all()
    serializer_class = HseReportDoxSerializers
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=['get'])
    def contractList(self, request, *args, **kwargs):
        """Get all HSE report documents for a contract."""
        contract_id = int(kwargs["contractid"])
        
        documents = HseReportDoxService.get_contract_documents(contract_id)
        serializer = HseReportDoxSerializers(instance=documents, many=True)
        
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def download(self, request, *args, **kwargs):
        """Download an HSE report document."""
        document_id = int(kwargs["id"])
        
        document = HseReportDoxService.get_document_for_download(document_id)
        
        if not document.file:
            return Response(
                {"status": "error", "data": "file not exist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response = FileDownloadService.create_file_response(
            document.file, document.filename
        )
        return response


class ProjectDoxAPI(viewsets.ModelViewSet):
    """API for the ProjectDox model."""
    
    queryset = ProjectDox.objects.all()
    serializer_class = ProjectDoxSerializers
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=['get'])
    def contractList(self, request, *args, **kwargs):
        """Get all project documents for a contract."""
        user_id = int(kwargs["userid"])
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        report_id = int(kwargs["reportid"])
        
        documents = ProjectDoxService.get_contract_documents(
            user_id, contract_id, date_id, report_id
        )
        serializer = ProjectDoxSerializers(instance=documents, many=True)
        
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def download(self, request, *args, **kwargs):
        """Download a project document."""
        document_id = int(kwargs["id"])
        
        document = ProjectDoxService.get_document_for_download(document_id)
        
        if not document.file:
            return Response(
                {"status": "error", "data": "file not exist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response = FileDownloadService.create_file_response(
            document.file, document.filename
        )
        return response


class ContractorDoxAPI(viewsets.ModelViewSet):
    """API for the ContractorDox model."""
    
    queryset = ContractorDox.objects.all()
    serializer_class = ContractorDoxSerializers
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=['get'])
    def contractList(self, request, *args, **kwargs):
        """Get all contractor documents for a contract."""
        contract_id = int(kwargs["contractid"])
        
        documents = ContractorDoxService.get_contract_documents(contract_id)
        serializer = ContractorDoxSerializers(instance=documents, many=True)
        
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def download(self, request, *args, **kwargs):
        """Download a contractor document."""
        document_id = int(kwargs["id"])
        
        document = ContractorDoxService.get_document_for_download(document_id)
        
        if not document.file:
            return Response(
                {"status": "error", "data": "file not exist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response = FileDownloadService.create_file_response(
            document.file, document.filename
        )
        return response


class ProjectMonthlyDoxAPI(viewsets.ModelViewSet):
    """API for the ProjectMonthlyDox model."""
    
    queryset = ProjectMonthlyDox.objects.all()
    serializer_class = ProjectMonthlyDoxSerializers
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=['get'])
    def contractList(self, request, *args, **kwargs):
        """Get all project monthly documents for a contract."""
        user_id = int(kwargs["userid"])
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        report_id = int(kwargs["reportid"])
        
        documents = ProjectMonthlyDoxService.get_contract_documents(
            user_id, contract_id, date_id, report_id
        )
        serializer = ProjectMonthlyDoxSerializers(instance=documents, many=True)
        
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def download(self, request, *args, **kwargs):
        """Download a project monthly document."""
        document_id = int(kwargs["id"])
        
        document = ProjectMonthlyDoxService.get_document_for_download(document_id)
        
        if not document.file:
            return Response(
                {"status": "error", "data": "file not exist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response = FileDownloadService.create_file_response(
            document.file, document.filename
        )
        return response


class ApprovedInvoiceDoxAPI(viewsets.ModelViewSet):
    """API for the ApprovedInvoiceDox model."""
    
    queryset = InvoiceDox.objects.all()
    serializer_class = ApprovedInvoiceDoxSerializers
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=['get'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get all approved invoice documents for a contract."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        documents = ApprovedInvoiceDoxService.get_contract_month_documents(
            contract_id, date_id
        )
        serializer = ApprovedInvoiceDoxSerializers(instance=documents, many=True)
        
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def download(self, request, *args, **kwargs):
        """Download an approved invoice document."""
        document_id = int(kwargs["id"])
        
        document = ApprovedInvoiceDoxService.get_document_for_download(document_id)
        
        if not document.file:
            return Response(
                {"status": "error", "data": "file not exist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response = FileDownloadService.create_file_response(
            document.file, document.filename
        )
        return response


class ReportDoxAPI(APIView):
    """API for the ReportDox model."""
    
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, format=None):
        """Get all report documents."""
        report_dox = ReportDoxService.get_all_documents()
        serializer = ReportDoxSerializers(data=report_dox, many=True)
        
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def post(self, request, format=None):
        """Create a new report document."""
        serializer = ReportDoxSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )


class ZoneAPI(viewsets.ModelViewSet):
    """API for the Zone model."""
    
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializers
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def contractZoneList(self, request, *args, **kwargs):
        """Get all zones for a contract."""
        contract_id = int(kwargs["contractid"])
        
        zones = ZoneService.get_contract_zones(contract_id)
        serializer = ZoneSerializers(instance=zones, many=True)
        
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )


@api_view(['post'])
@permission_classes([permissions.IsAuthenticated])
def getContractZoneImages(request):
    """Get or create zone images for a contract and date."""
    data = request.data
    user_id = int(data["userid"])
    contract_id = int(data["contractid"])
    date_id = int(data["dateid"])
    report_id = int(data["reportid"])
    
    zone_images = ZoneImageService.get_or_create_contract_zone_images(
        user_id, contract_id, date_id, report_id
    )
    serializer = ZoneImagesSerializers(instance=zone_images, many=True)
    
    return Response(
        {"status": "success", "data": serializer.data},
        status=status.HTTP_200_OK
    )


@api_view(['put'])
@permission_classes([permissions.IsAuthenticated])
def updateZoneImage(request, pk):
    """Update a zone image."""
    data = request.data
    contract_id = int(data['contractid'])
    zone = str(data['zone'])
    date_id = data['dateid']
    ppp = data['ppp']
    app = data['app']
    image1 = data.get('img1')
    description1 = data['description1']
    image2 = data.get('img2')
    description2 = data['description2']
    image3 = data.get('img3')
    description3 = data['description3']
    
    zone_image = ZoneImageService.update_zone_image(
        pk, contract_id, zone, date_id, ppp, app,
        image1, description1, image2, description2, image3, description3
    )
    
    serializer = ZoneImagesSerializers(zone_image, many=False)
    return Response(
        {"status": "success", "data": serializer.data},
        status=status.HTTP_200_OK
    )


class ZoneImagesAPI(APIView):
    """API for the ZoneImages model."""
    
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, *args, **kwargs):
        """Get zone images for a contract and date."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        zone_images = ZoneImageService.get_or_create_contract_zone_images(
            None, contract_id, date_id, None
        )
        serializer = ZoneImagesSerializers(instance=zone_images, many=True)
        
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def post(self, request, format=None):
        """Create a new zone image."""
        data = request.data
        contract_id = int(data['contractid'])
        zone = str(data['zone'])
        date_id = data['dateid']
        ppp = data['ppp']
        app = data['app']
        img1 = data.get('img1')
        description1 = data['description1']
        img2 = data.get('img2')
        description2 = data['description2']
        img3 = data.get('img3')
        description3 = data['description3']
        
        zone_image = ZoneImageService.create_zone_image(
            contract_id, zone, date_id, ppp, app,
            img1, description1, img2, description2, img3, description3
        )
        
        serializer = ZoneImagesSerializers(zone_image, many=False)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )
    
    def put(self, request, pk, format=None):
        """Update an existing zone image."""
        data = request.data
        contract_id = int(data['contractid'])
        zone = str(data['zone'])
        date_id = data['dateid']
        ppp = data['ppp']
        app = data['app']
        image1 = data.get('img1')
        description1 = data['description1']
        image2 = data.get('img2')
        description2 = data['description2']
        image3 = data.get('img3')
        description3 = data['description3']
        
        zone_image = ZoneImageService.update_zone_image(
            pk, contract_id, zone, date_id, ppp, app,
            image1, description1, image2, description2, image3, description3
        )
        
        serializer = ZoneImagesSerializers(zone_image, many=False)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )
    
    def delete(self, request, pk, format=None):
        """Delete a zone image."""
        ZoneImageService.delete_zone_image(pk)
        
        return Response(
            {"status": "success"},
            status=status.HTTP_200_OK
        )


@api_view(['get'])
@permission_classes([permissions.IsAuthenticated])
def getReportProjectZoneImages(request, zoneid):
    """Get all images for a specific zone."""
    zone_images = ZoneImageService.get_project_zone_images(zoneid)
    serializer = ProjectZoneImagesSerializers(instance=zone_images, many=True)
    
    return Response(
        {"status": "success", "data": serializer.data},
        status=status.HTTP_200_OK
    )


@api_view(['post'])
@permission_classes([permissions.IsAuthenticated])
def getReportSelectedProjectAllZonesImages(request, *args, **kwargs):
    """Get zone images for selected projects at a specific date."""
    data = request.data
    contract_ids = [int(contract_id) for contract_id in data]
    date_id = int(kwargs["dateid"])
    
    zone_images = ZoneImageService.get_selected_projects_all_zones_images(
        contract_ids, date_id
    )
    serializer = ProjectZoneImagesSerializers(instance=zone_images, many=True)
    
    return Response(
        {"status": "success", "data": serializer.data},
        status=status.HTTP_200_OK
    )


@api_view(['post'])
@permission_classes([permissions.IsAuthenticated])
def getReportSelectedProjectAllZonesImagesEx(request, *args, **kwargs):
    """Get zone images for selected projects within a date range."""
    data = request.data
    contract_ids = [int(contract_id) for contract_id in data]
    from_date_id = int(kwargs["fromDateid"])
    to_date_id = int(kwargs["toDateid"])
    
    zone_images = ZoneImageService.get_selected_projects_all_zones_images_range(
        contract_ids, from_date_id, to_date_id
    )
    serializer = ProjectZoneImagesSerializers(instance=zone_images, many=True)
    
    return Response(
        {"status": "success", "data": serializer.data},
        status=status.HTTP_200_OK
    )


@api_view(['get'])
@permission_classes([permissions.IsAuthenticated])
def getReportAllProjectZonesImages(request, *args, **kwargs):
    """Get zone images for all projects at a specific date."""
    date_id = int(kwargs["dateid"])
    
    zone_images = ZoneImageService.get_all_projects_zones_images(date_id)
    serializer = ProjectZoneImagesSerializers(instance=zone_images, many=True)
    
    return Response(
        {"status": "success", "data": serializer.data},
        status=status.HTTP_200_OK
    )


@api_view(['get'])
@permission_classes([permissions.IsAuthenticated])
def getReportAllProjectZonesImagesEx(request, *args, **kwargs):
    """Get zone images for all projects within a date range."""
    from_date_id = int(kwargs["fromDateid"])
    to_date_id = int(kwargs["toDateid"])
    
    zone_images = ZoneImageService.get_all_projects_zones_images_range(
        from_date_id, to_date_id
    )
    serializer = ProjectZoneImagesSerializers(instance=zone_images, many=True)
    
    return Response(
        {"status": "success", "data": serializer.data},
        status=status.HTTP_200_OK
    )


class ReportVisitAPI(APIView):
    """API for the ReportVisit model."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, *args, **kwargs):
        """Get report visits for a contract and date."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        report_visits = ReportVisitService.get_contract_date_visits(
            contract_id, date_id
        )
        serializer = ReportVisitSerializers(instance=report_visits, many=True)
        
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def post(self, request):
        """Create or update a report visit."""
        data = request.data
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        user_id = int(data["userid"])
        report_id = int(data["reportid"])
        
        ReportVisitService.create_report_visit(
            contract_id, date_id, user_id, report_id
        )
        
        return Response(
            {"status": "success"},
            status=status.HTTP_200_OK
        )
        