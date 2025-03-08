import mimetypes
from django.http import FileResponse
from django.db.models import Max, Q, F
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from accounts.models import UserRole

from projects_files.models import *
from projects_files.serializers import *
from projects_files.services import SetReportVisit


class HseReportDoxAPI(viewsets.ModelViewSet):
    queryset = HseReportDox.objects.all()
    serializer_class = HseReportDoxSerializers
    permission_classes = [
        permissions.IsAuthenticated
    ]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=['get'])
    def contractList(self, request, *args, **kwargs):
        try:
            contractId = int(kwargs["contractid"])
            hseReportDox = HseReportDox.objects.filter(contractid__exact=contractId)
            serializer = HseReportDoxSerializers(instance=hseReportDox, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def download(self, request, *args, **kwargs):
        try:
            id = int(kwargs["id"])
            hseReportDox = HseReportDox.objects.get(pk=id)
            if hseReportDox.file:
                storage, path = hseReportDox.file.storage, hseReportDox.file.path
                mimetype, _ = mimetypes.guess_type(hseReportDox.file.path)
                # file_handle = hseReportDox.file.open(path)
                response = FileResponse(storage.open(path, 'rb'), content_type=mimetype)
                response['Content-Length'] = hseReportDox.file.size
                response['Content-Disposition'] = "attachment; filename={}".format(hseReportDox.filename)
                return response    
            return Response({"status": "error", "data": "file not exist" }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # @action(detail=False, methods=['patch'])
    # def partialUpdate(self, request, *args, **kwargs):
    #     try:
    #         id = int(kwargs["id"])
    #         description = request.data['description']
    #         hseReportDox = HseReportDox.objects.get(pk=id)
    #         hseReportDox.description = description
    #         hseReportDox.save()   
    #         hseReportDox = HseReportDox.objects.get(pk=id)
    #         serializer = HseReportDoxSerializers(instance=hseReportDox, many=False)
    #         return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # @action(detail=False, methods=['put'])
    # def conditionalUpdate1(self, request, *args, **kwargs):
    #     try:
    #         id = int(kwargs["id"])
    #         file = request.data["file"] 
    #         # if hasattr(request.data, 'file') else None

    #         # hseReportDox = HseReportDox.objects.get(pk=id)
    #         # serializer = HseReportDoxSerializers(instance=hseReportDox, data=request.data)
    #         # serializer.is_valid(raise_exception=True)
    #         # if file.name != hseReportDox.file.name:
    #         #     serializer.save()
    #         # else:
    #         #     serializer.save(file=hseReportDox.file)
    #         # return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    #         hseReportDox = HseReportDox.objects.get(pk=id)
    #         if file and file.name != hseReportDox.filename:
    #             # _file is not None:
    #             serializer = HseReportDoxSerializers(instance=hseReportDox, data=request.data)
    #             serializer.is_valid(raise_exception=True)
    #             serializer.save()
    #             return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    #         else:
    #             description = request['description']
    #             hseReportDox.description = description
    #             hseReportDox.save()   
    #             hseReportDox = HseReportDox.objects.get(pk=id)
    #             serializer = HseReportDoxSerializers(instance=hseReportDox, many=False)
    #             return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
# class HseReportDoxAPI1(APIView):
#     permission_classes = [
#         permissions.IsAuthenticated
#     ]
#     parser_classes = [MultiPartParser, FormParser]

#     def get(self, format=None):
#         try:
#             reportDox = HseReportDox.objects.all()
#             serializer = HseReportDoxSerializers(reportDox)
#             return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def post(self, request, format=None):
#         try:
#             serializer = HseReportDoxSerializers(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def put(self, request, pk, format=None):
#         try:
#             reportDox = HseReportDox.objects.get(pk=pk)
#             serializer = HseReportDoxSerializers(instance=reportDox, data=request.data, partial=True)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def delete(self, request, pk, format=None):
#         try:
#             reportDox = HseReportDox.objects.get(pk=pk)
#             reportDox.delete()    
#             return Response({"status": "success"}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProjectDoxAPI(viewsets.ModelViewSet):
    queryset = ProjectDox.objects.all()
    serializer_class = ProjectDoxSerializers
    permission_classes = [
        permissions.IsAuthenticated
    ]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=['get'])
    def contractList(self, request, *args, **kwargs):
        try:
            # data = request.data
            userId = int(kwargs["userid"])
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
            reportId = int(kwargs["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
            
            projectDox = ProjectDox.objects.filter(contractid__exact=contractId, dateid__lte=dateId)
            serializer = ProjectDoxSerializers(instance=projectDox, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def download(self, request, *args, **kwargs):
        try:
            id = int(kwargs["id"])
            projectDox = ProjectDox.objects.get(pk=id)
            if projectDox.file:
                storage, path = projectDox.file.storage, projectDox.file.path
                mimetype, _ = mimetypes.guess_type(projectDox.file.path)
                # file_handle = projectDox.file.open(path)
                response = FileResponse(storage.open(path, 'rb'), content_type=mimetype)
                response['Content-Length'] = projectDox.file.size
                response['Content-Disposition'] = "attachment; filename={}".format(projectDox.filename)
                return response    
            return Response({"status": "error", "data": "file not exist" }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
class ContractorDoxAPI(viewsets.ModelViewSet):
    queryset = ContractorDox.objects.all()
    serializer_class = ContractorDoxSerializers
    permission_classes = [
        permissions.IsAuthenticated
    ]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=['get'])
    def contractList(self, request, *args, **kwargs):
        try:
            contractId = int(kwargs["contractid"])
            contractorDox = ContractorDox.objects.filter(contractid__exact=contractId)
            serializer = ContractorDoxSerializers(instance=contractorDox, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def download(self, request, *args, **kwargs):
        try:
            id = int(kwargs["id"])
            contractorDox = ContractorDox.objects.get(pk=id)
            if contractorDox.file:
                storage, path = contractorDox.file.storage, contractorDox.file.path
                mimetype, _ = mimetypes.guess_type(contractorDox.file.path)
                # file_handle = contractorDox.file.open(path)
                response = FileResponse(storage.open(path, 'rb'), content_type=mimetype)
                response['Content-Length'] = contractorDox.file.size
                response['Content-Disposition'] = "attachment; filename={}".format(contractorDox.filename)
                return response    
            return Response({"status": "error", "data": "file not exist" }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
class ProjectMonthlyDoxAPI(viewsets.ModelViewSet):
    queryset = ProjectMonthlyDox.objects.all()
    serializer_class = ProjectMonthlyDoxSerializers
    permission_classes = [
        permissions.IsAuthenticated
    ]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=['get'])
    def contractList(self, request, *args, **kwargs):
        try:
            # data = request.data
            userId = int(kwargs["userid"])
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
            reportId = int(kwargs["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
            
            projectMonthlyDox = ProjectMonthlyDox.objects.filter(contractid__exact=contractId, dateid__lte=dateId)
            serializer = ProjectMonthlyDoxSerializers(instance=projectMonthlyDox, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def download(self, request, *args, **kwargs):
        try:
            id = int(kwargs["id"])
            projectMonthlyDox = ProjectMonthlyDox.objects.get(pk=id)
            if projectMonthlyDox.file:
                storage, path = projectMonthlyDox.file.storage, projectMonthlyDox.file.path
                mimetype, _ = mimetypes.guess_type(projectMonthlyDox.file.path)
                # file_handle = projectMonthlyDox.file.open(path)
                response = FileResponse(storage.open(path, 'rb'), content_type=mimetype)
                response['Content-Length'] = projectMonthlyDox.file.size
                response['Content-Disposition'] = "attachment; filename={}".format(projectMonthlyDox.filename)
                return response    
            return Response({"status": "error", "data": "file not exist" }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
class ApprovedInvoiceDoxAPI(viewsets.ModelViewSet):
    queryset = InvoiceDox.objects.all()
    serializer_class = ApprovedInvoiceDoxSerializers
    permission_classes = [
        permissions.IsAuthenticated
    ]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=['get'])
    def contractMonthList(self, request, *args, **kwargs):
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
            approvedInvoiceDox = InvoiceDox.objects.filter(contractid__exact=contractId, dateid__lte=dateId)
            serializer = ApprovedInvoiceDoxSerializers(instance=approvedInvoiceDox, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def download(self, request, *args, **kwargs):
        try:
            id = int(kwargs["id"])
            approvedInvoiceDox = InvoiceDox.objects.get(pk=id)
            if approvedInvoiceDox.file:
                storage, path = approvedInvoiceDox.file.storage, approvedInvoiceDox.file.path
                mimetype, _ = mimetypes.guess_type(approvedInvoiceDox.file.path)
                # file_handle = approvedInvoiceDox.file.open(path)
                response = FileResponse(storage.open(path, 'rb'), content_type=mimetype)
                response['Content-Length'] = approvedInvoiceDox.file.size
                response['Content-Disposition'] = "attachment; filename={}".format(approvedInvoiceDox.filename)
                return response    
            return Response({"status": "error", "data": "file not exist" }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
class ReportDoxAPI(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, format=None):
        try:
            reportDox = ReportDox.objects.all()
            serializer = ReportDoxSerializers(data=reportDox)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request, format=None):
        try:
            serializer = ReportDoxSerializers(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ZoneAPI(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializers
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['get'])
    def contractZoneList(self, request, *args, **kwargs):
        try:
            contractId = int(kwargs["contractid"])
            zones = Zone.objects.filter(contractid__exact=contractId)
            serializer = ZoneSerializers(instance=zones, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 
@api_view(['post'])
@permission_classes([permissions.IsAuthenticated])
def getContractZoneImages(request):
    try:
        data = request.data
        userId = int(data["userid"])
        contractId = int(data["contractid"])
        dateId = int(data["dateid"])
        reportId = int(data["reportid"])
        
        SetReportVisit(userId, contractId, dateId, reportId) 
               
        last_dateId = ReportDate.objects.filter(dateid__lt=dateId).aggregate(Max('dateid'))['dateid__max']
        
        count = ZoneImage.objects.filter(zoneid__contractid__exact=contractId, dateid__exact=dateId)
        
        if count == 0:
            zones = Zone.objects.filter(contractid__exact=contractId, Zone_Zoneimage__dateid__exact=last_dateId) 
                                            #  dateid__exact=last_dateId).exclude(Q(img1__exact=None) | 
                                            #                            Q(img2__exact=None) | 
                                            #                            Q(img3__exact=None)).values('zoneid')
        
            date = ReportDate.objects.get(pk=dateId)
            for zone in zones:
                ZoneImage.objects.create(zoneid=zone, dateid=date)
            
        zoneImage = ZoneImage.objects.filter(zoneid__contractid__exact=contractId, dateid__exact=dateId)
        serializer = ZoneImagesSerializers(instance=zoneImage, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['put'])
@permission_classes([permissions.IsAuthenticated])
def updateZoneImage(request, pk):
    try:
        id = pk
        data = request.data
        contractId = int(data['contractid'])
        zone = str(data['zone'])
        dateId = data['dateid']
        ppp = data['ppp']
        app = data['app']
        image1 = data['img1'] if 'img1' in data else None
        description1 = data['description1']
        image2 = data['img2'] if 'img2' in data else None
        description2 = data['description2']
        image3 = data['img3'] if 'img3' in data else None
        description3 = data['description3']
        
        zoneObj = None
        count = Zone.objects.filter(contractid__exact=contractId, zone__exact=zone).count()
        if count == 0:
            contract = Contract.objects.get(pk=contractId)
            zoneObj = Zone.objects.create(contractid=contract, zone=zone)
        else:
            zoneObj = Zone.objects.get(contractid=contractId, zone=zone)
            
        date = ReportDate.objects.get(pk=dateId)
        zoneimage = ZoneImage.objects.get(pk=id)
        zoneimage.zoneid = zoneObj
        zoneimage.dateid = date
        zoneimage.ppp = ppp
        zoneimage.app = app
        if image1 and image1 is not None :
            zoneimage.img1 = image1
        zoneimage.description1 = description1
        if image2 and image2 is not None :
            zoneimage.img2 = image2
        zoneimage.description2 = description2
        if image3 and image3 is not None :
            zoneimage.img3 = image3
        zoneimage.description3 = description3
        zoneimage.save()
        
        serializer = ZoneImagesSerializers(zoneimage, many=False)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class ZoneImagesAPI(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, *args, **kwargs):
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
            
            last_dateId = ReportDate.objects.filter(dateid__lt=dateId).aggregate(Max('dateid'))['dateid__max']
            
            count = ZoneImage.objects.filter(zoneid__contractid__exact=contractId, dateid__exact=dateId)
            
            if count == 0:
                zones = Zone.objects.filter(contractid__exact=contractId, Zone_Zoneimage__dateid__exact=last_dateId) 
                                                #  dateid__exact=last_dateId).exclude(Q(img1__exact=None) | 
                                                #                            Q(img2__exact=None) | 
                                                #                            Q(img3__exact=None)).values('zoneid')
            
                date = ReportDate.objects.get(pk=dateId)
                for zone in zones:
                    ZoneImage.objects.create(zoneid=zone, dateid=date)
                
            zoneImage = ZoneImage.objects.filter(zoneid__contractid__exact=contractId, dateid__exact=dateId)
            serializer = ZoneImagesSerializers(instance=zoneImage, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, format=None):
        try:
            data = request.data
            contractId = int(data['contractid'])
            zone = str(data['zone'])
            dateId = data['dateid']
            ppp = data['ppp']
            app = data['app']
            img1 = data['img1'] if 'img1' in data else None
            description1 = data['description1']
            img2 = data['img2'] if 'img2' in data else None
            description2 = data['description2']
            img3 = data['img3'] if 'img3' in data else None
            description3 = data['description3']
            
            zoneObj = None
            count = Zone.objects.filter(contractid__exact=contractId, zone__exact=zone).count()
            if count == 0:
                contract = Contract.objects.get(pk=contractId)
                zoneObj = Zone.objects.create(contractid=contract, zone=zone)
            else:
                zoneObj = Zone.objects.get(contractid=contractId, zone=zone)
                
            date = ReportDate.objects.get(pk=dateId)
            zoneimage = ZoneImage.objects.create(zoneid=zoneObj, dateid=date, ppp =ppp, app= app, 
                                                 img1=img1, description1=description1, 
                                                 img2=img2, description2=description2, 
                                                 img3=img3, description3=description3)
            
            serializer = ZoneImagesSerializers(zoneimage, many=False)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, pk, format=None):
        try:
            id = pk
            data = request.data
            contractId = int(data['contractid'])
            zone = str(data['zone'])
            dateId = data['dateid']
            ppp = data['ppp']
            app = data['app']
            image1 = data['img1'] if 'img1' in data else None
            description1 = data['description1']
            image2 = data['img2'] if 'img2' in data else None
            description2 = data['description2']
            image3 = data['img3'] if 'img3' in data else None
            description3 = data['description3']
            
            zoneObj = None
            count = Zone.objects.filter(contractid__exact=contractId, zone__exact=zone).count()
            if count == 0:
                contract = Contract.objects.get(pk=contractId)
                zoneObj = Zone.objects.create(contractid=contract, zone=zone)
            else:
                zoneObj = Zone.objects.get(contractid=contractId, zone=zone)
                
            date = ReportDate.objects.get(pk=dateId)
            zoneimage = ZoneImage.objects.get(pk=id)
            zoneimage.zoneid = zoneObj
            zoneimage.dateid = date
            zoneimage.ppp = ppp
            zoneimage.app = app
            if image1 and image1 is not None :
                zoneimage.img1 = image1
            zoneimage.description1 = description1
            if image2 and image2 is not None :
                zoneimage.img2 = image2
            zoneimage.description2 = description2
            if image3 and image3 is not None :
                zoneimage.img3 = image3
            zoneimage.description3 = description3
            zoneimage.save()
            
            serializer = ZoneImagesSerializers(zoneimage, many=False)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, pk, format=None):
        try:
            id = pk
            zoneimage = ZoneImage.objects.get(pk=id)
            zoneId = zoneimage.zoneid.pk
            zoneimage.delete()
            
            flg = ZoneImage.objects.filter(zoneid__exact=zoneId).count()
            if flg == 0:
                zone = Zone.objects.get(pk=zoneId)
                zone.delete()
                
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    # @action(detail=True, methods=['get'])
    # def monthList(self, request, *args, **kwargs):
    #     try:
    #         contractId = int(kwargs["contract_id"])
    #         dateId = int(kwargs["date_id"])
            
    #         last_dateId = ReportDate.objects.filter(dateid__lt=dateId).aggregate(Max('dateid'))['dateid__max']
            
    #         count = ZoneImage.objects.filter(zoneid__contractid__exact=contractId, dateid__exact=dateId)
            
    #         if count == 0:
    #             zones = Zone.objects.filter(contractid__exact=contractId, zoneimage__dateid__exact=last_dateId) 
    #                                             #  dateid__exact=last_dateId).exclude(Q(img1__exact=None) | 
    #                                             #                            Q(img2__exact=None) | 
    #                                             #                            Q(img3__exact=None)).values('zoneid')
            
    #             date = ReportDate.objects.get(pk=dateId)
    #             for zone in zones:
    #                 ZoneImage.objects.create(zoneid=zone, dateid=date)
                
    #         zoneImage = ZoneImage.objects.filter(zone__contractid__exact=contractId, dateid__exact=dateId)
    #         serializer = ZoneSerializers(instance=zoneImage, many=True)
    #         return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['get'])
@permission_classes([permissions.IsAuthenticated])
def getReportProjectZoneImages(request, zoneid):
    try:
        zoneId = zoneid
        zoneImages = ZoneImage.projectZoneImages.projectZoneImages(zoneId)
        serializer = ProjectZoneImagesSerializers(instance=zoneImages, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['post'])
@permission_classes([permissions.IsAuthenticated])
def getReportSelectedProjectAllZonesImages(request, *args, **kwargs):
    try: 
        data = request.data
        contractsId = [int(contractId) for contractId in data]
        dateId = int(kwargs["dateid"])
        
        zoneImages = ZoneImage.projectZoneImages.selectedProjectAllZonesImages(contractsId, dateId)
        serializer = ProjectZoneImagesSerializers(instance=zoneImages, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['post'])
@permission_classes([permissions.IsAuthenticated])
def getReportSelectedProjectAllZonesImagesEx(request, *args, **kwargs):
    try: 
        data = request.data
        contractsId = [int(contractId) for contractId in data]
        fromDateId = int(kwargs["fromDateid"])
        toDateId = int(kwargs["toDateid"])
        
        zoneImages = ZoneImage.projectZoneImages.selectedProjectAllZonesImagesEx(contractsId, fromDateId, toDateId)
        serializer = ProjectZoneImagesSerializers(instance=zoneImages, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['get'])
@permission_classes([permissions.IsAuthenticated])
def getReportAllProjectZonesImages(request, *args, **kwargs):
    try:
        dateId = int(kwargs["dateid"])

        zoneImages = ZoneImage.projectZoneImages.allProjectZonesImages(dateId)
        serializer = ProjectZoneImagesSerializers(instance=zoneImages, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['get'])
@permission_classes([permissions.IsAuthenticated])
def getReportAllProjectZonesImagesEx(request, *args, **kwargs):
    try:
        fromDateId = int(kwargs["fromDateid"])
        toDateId = int(kwargs["toDateid"])
        
        zoneImages = ZoneImage.projectZoneImages.allProjectZonesImagesEx(fromDateId, toDateId)
        serializer = ProjectZoneImagesSerializers(instance=zoneImages, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReportVisitAPI(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, *args, **kwargs):
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
                        
            reportVisits = ReportVisit.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            
            serializer = ReportVisitSerializers(instance=reportVisits, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def post(self, request):
        try:
            data = request.data
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            userId = int(data["userid"])
            reportId = int(data["reportid"])
            
            user = get_user_model().objects.get(pk=userId)
            date = ReportDate.objects.get(pk=dateId)

            if(contractId == -1):
                reportVisits = ReportVisit.objects.filter(userid__exact=userId, dateid__exact=dateId)
                reportVisits.update(imagereport=1)
                
                isAllProject = UserRole.objects.filter(userid__exact=userId, contractid__exact=None).count() > 0
                
                if isAllProject:
                    contracts = Contract.objects.filter(iscompleted__exact=False).exclude(contractid__in=reportVisits)
                    for contract in contracts:
                        ReportVisit.objects.update_or_create(contractid=contract, dateid=date, userid=user, imagereport=1)
                else:
                    userContractRole = UserRole.objects.filter(userid__exact=userId)
                    contracts = Contract.objects.filter(contractid__in=userContractRole).exclude(contractid__in=reportVisits)
                    for contract in contracts:
                        ReportVisit.objects.update_or_create(contractid=contract, dateid=date, userid=user, imagereport=1)
            else: 
                contracts = Contract.objects.filter(contractid__exact=contractId)
                if len(contracts) == 1:
                        if reportId == 1:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "financialinfo": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId}) 
  
                        elif reportId == 2:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "hse": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId}) 
 
                        elif reportId == 3:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "progressstate": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId}) 
 
                        elif reportId == 4:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "timeprogressstate": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId}) 
 
                        elif reportId == 5:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "invoice": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId}) 
 
                        elif reportId == 6:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "financialinvoice": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId}) 
  
                        elif reportId == 7:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "workvolume": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId}) 
            
                        elif reportId == 8:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "pmsprogress": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId}) 
                            
                        elif reportId == 9:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "budget": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId}) 

                        elif reportId == 10:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "machinary": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId}) 
 
                        elif reportId == 11:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "personel": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId})
 
                        elif reportId == 12:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "problems": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId})
       
                        elif reportId == 13:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "criticalactions": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId})

                        elif reportId == 14:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "zoneimages": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId})
                            
                        elif reportId == 15:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "projectdox": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId})
                            
                        elif reportId == 16:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "durationdox": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId})

                        elif reportId == 17:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "dashboard_r": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId})

                        elif reportId == 18:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "dashboard_fc": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId})
                            
                        elif reportId == 19:
                            reportVisit, _ = ReportVisit.objects.update_or_create(
                                contractid=contracts[0], dateid=date, userid=user, 
                                defaults={"contractid": contracts[0], "dateid": date, "userid": user, "imagereport": 1})

                            ReportVisitdate.objects.update_or_create(
                                visitreportid=reportVisit, reportid=reportId,
                                defaults={"visitreportid":reportVisit, "reportid":reportId})
                                             
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
