"""
Services for the projects_files application.
Contains all business logic separated from API views.
"""
import mimetypes
from django.contrib.auth import get_user_model
from django.db.models import Max
from django.http import FileResponse

from accounts.models import UserRole
from contracts.models import Contract
from projects.models import ReportDate
from projects_files.models import (
    HseReportDox, ProjectDox, ContractorDox, ProjectMonthlyDox,
    InvoiceDox, ReportDox, Zone, ZoneImage, ReportVisit, ReportVisitdate
)


class FileDownloadService:
    """Service for handling file downloads."""
    
    @staticmethod
    def create_file_response(file_obj, filename):
        """
        Create a FileResponse for downloading a file.
        
        Args:
            file_obj: File field object from model
            filename: Name to use for downloaded file
            
        Returns:
            FileResponse or None if file doesn't exist
        """
        if not file_obj:
            return None
            
        storage, path = file_obj.storage, file_obj.path
        mimetype, _ = mimetypes.guess_type(file_obj.path)
        
        response = FileResponse(storage.open(path, 'rb'), content_type=mimetype)
        response['Content-Length'] = file_obj.size
        response['Content-Disposition'] = f"attachment; filename={filename}"
        
        return response


class HseReportDoxService:
    """Service for managing HSE report documents."""
    
    @staticmethod
    def get_contract_documents(contract_id):
        """Get all HSE report documents for a contract."""
        return HseReportDox.objects.filter(contractid__exact=contract_id)
    
    @staticmethod
    def get_document_for_download(document_id):
        """Get HSE report document for download."""
        return HseReportDox.objects.get(pk=document_id)


class ProjectDoxService:
    """Service for managing project documents."""
    
    @staticmethod
    def get_contract_documents(user_id, contract_id, date_id, report_id):
        """Get all project documents for a contract up to a specific date."""
        ReportVisitService.set_report_visit(user_id, contract_id, date_id, report_id)
        return ProjectDox.objects.filter(
            contractid__exact=contract_id,
            dateid__lte=date_id
        )
    
    @staticmethod
    def get_document_for_download(document_id):
        """Get project document for download."""
        return ProjectDox.objects.get(pk=document_id)


class ContractorDoxService:
    """Service for managing contractor documents."""
    
    @staticmethod
    def get_contract_documents(contract_id):
        """Get all contractor documents for a contract."""
        return ContractorDox.objects.filter(contractid__exact=contract_id)
    
    @staticmethod
    def get_document_for_download(document_id):
        """Get contractor document for download."""
        return ContractorDox.objects.get(pk=document_id)


class ProjectMonthlyDoxService:
    """Service for managing project monthly documents."""
    
    @staticmethod
    def get_contract_documents(user_id, contract_id, date_id, report_id):
        """Get all project monthly documents for a contract up to a specific date."""
        ReportVisitService.set_report_visit(user_id, contract_id, date_id, report_id)
        return ProjectMonthlyDox.objects.filter(
            contractid__exact=contract_id,
            dateid__lte=date_id
        )
    
    @staticmethod
    def get_document_for_download(document_id):
        """Get project monthly document for download."""
        return ProjectMonthlyDox.objects.get(pk=document_id)


class ApprovedInvoiceDoxService:
    """Service for managing approved invoice documents."""
    
    @staticmethod
    def get_contract_month_documents(contract_id, date_id):
        """Get all approved invoice documents for a contract up to a specific date."""
        return InvoiceDox.objects.filter(
            contractid__exact=contract_id,
            dateid__lte=date_id
        )
    
    @staticmethod
    def get_document_for_download(document_id):
        """Get approved invoice document for download."""
        return InvoiceDox.objects.get(pk=document_id)


class ReportDoxService:
    """Service for managing report documents."""
    
    @staticmethod
    def get_all_documents():
        """Get all report documents."""
        return ReportDox.objects.all()
    
    @staticmethod
    def create_document(data):
        """Create a new report document."""
        return ReportDox.objects.create(**data)


class ZoneService:
    """Service for managing zones."""
    
    @staticmethod
    def get_contract_zones(contract_id):
        """Get all zones for a contract."""
        return Zone.objects.filter(contractid__exact=contract_id)
    
    @staticmethod
    def get_or_create_zone(contract_id, zone_name):
        """
        Get existing zone or create new one.
        
        Returns:
            Zone object
        """
        zone_exists = Zone.objects.filter(
            contractid__exact=contract_id,
            zone__exact=zone_name
        ).exists()
        
        if not zone_exists:
            contract = Contract.objects.get(pk=contract_id)
            return Zone.objects.create(contractid=contract, zone=zone_name)
        
        return Zone.objects.get(contractid=contract_id, zone=zone_name)


class ZoneImageService:
    """Service for managing zone images."""
    
    @staticmethod
    def get_or_create_contract_zone_images(user_id, contract_id, date_id, report_id):
        """
        Get or create zone images for a contract and date.
        If no images exist for the current date, copy from the previous date.
        """
        ReportVisitService.set_report_visit(user_id, contract_id, date_id, report_id)
        
        last_date_id = ReportDate.objects.filter(
            dateid__lt=date_id
        ).aggregate(Max('dateid'))['dateid__max']
        
        current_images_exist = ZoneImage.objects.filter(
            zoneid__contractid__exact=contract_id,
            dateid__exact=date_id
        ).exists()
        
        if not current_images_exist:
            # Copy zones from previous date
            zones = Zone.objects.filter(
                contractid__exact=contract_id,
                Zone_Zoneimage__dateid__exact=last_date_id
            )
            
            date = ReportDate.objects.get(pk=date_id)
            for zone in zones:
                ZoneImage.objects.create(zoneid=zone, dateid=date)
        
        return ZoneImage.objects.filter(
            zoneid__contractid__exact=contract_id,
            dateid__exact=date_id
        )
    
    @staticmethod
    def create_zone_image(contract_id, zone_name, date_id, ppp, app, 
                         img1, description1, img2, description2, img3, description3):
        """Create a new zone image."""
        zone = ZoneService.get_or_create_zone(contract_id, zone_name)
        date = ReportDate.objects.get(pk=date_id)
        
        return ZoneImage.objects.create(
            zoneid=zone,
            dateid=date,
            ppp=ppp,
            app=app,
            img1=img1,
            description1=description1,
            img2=img2,
            description2=description2,
            img3=img3,
            description3=description3
        )
    
    @staticmethod
    def update_zone_image(image_id, contract_id, zone_name, date_id, ppp, app,
                         img1, description1, img2, description2, img3, description3):
        """Update an existing zone image."""
        zone = ZoneService.get_or_create_zone(contract_id, zone_name)
        date = ReportDate.objects.get(pk=date_id)
        
        zone_image = ZoneImage.objects.get(pk=image_id)
        zone_image.zoneid = zone
        zone_image.dateid = date
        zone_image.ppp = ppp
        zone_image.app = app
        
        if img1 is not None:
            zone_image.img1 = img1
        zone_image.description1 = description1
        
        if img2 is not None:
            zone_image.img2 = img2
        zone_image.description2 = description2
        
        if img3 is not None:
            zone_image.img3 = img3
        zone_image.description3 = description3
        
        zone_image.save()
        return zone_image
    
    @staticmethod
    def delete_zone_image(image_id):
        """
        Delete a zone image.
        If this is the last image for the zone, delete the zone as well.
        """
        zone_image = ZoneImage.objects.get(pk=image_id)
        zone_id = zone_image.zoneid.pk
        zone_image.delete()
        
        # Check if zone has any remaining images
        remaining_images = ZoneImage.objects.filter(zoneid__exact=zone_id).count()
        if remaining_images == 0:
            zone = Zone.objects.get(pk=zone_id)
            zone.delete()
    
    @staticmethod
    def get_project_zone_images(zone_id):
        """Get all images for a specific zone across all dates."""
        return ZoneImage.projectZoneImages.projectZoneImages(zone_id)
    
    @staticmethod
    def get_selected_projects_all_zones_images(contract_ids, date_id):
        """Get all zone images for selected contracts at a specific date."""
        return ZoneImage.projectZoneImages.selectedProjectAllZonesImages(
            contract_ids, date_id
        )
    
    @staticmethod
    def get_selected_projects_all_zones_images_range(contract_ids, from_date_id, to_date_id):
        """Get all zone images for selected contracts within a date range."""
        return ZoneImage.projectZoneImages.selectedProjectAllZonesImagesEx(
            contract_ids, from_date_id, to_date_id
        )
    
    @staticmethod
    def get_all_projects_zones_images(date_id):
        """Get all zone images for all projects at a specific date."""
        return ZoneImage.projectZoneImages.allProjectZonesImages(date_id)
    
    @staticmethod
    def get_all_projects_zones_images_range(from_date_id, to_date_id):
        """Get all zone images for all projects within a date range."""
        return ZoneImage.projectZoneImages.allProjectZonesImagesEx(
            from_date_id, to_date_id
        )


class ReportVisitService:
    """Service for managing report visits."""
    
    @staticmethod
    def get_contract_date_visits(contract_id, date_id):
        """Get all report visits for a contract and date."""
        return ReportVisit.objects.filter(
            contractid__exact=contract_id,
            dateid__exact=date_id
        )
    
    @staticmethod
    def set_report_visit(user_id, contract_id, date_id, report_id):
        """
        Record a report visit by a user.
        Handles both single contract and all-projects scenarios.
        """
        is_manager = UserRole.objects.filter(
            userid__exact=user_id,
            roleid__role__exact='Board'
        ).count()
        
        if is_manager == 0:
            return False
        
        user = get_user_model().objects.get(pk=user_id)
        date = ReportDate.objects.get(pk=date_id)

        if contract_id == -1:
            # Handle all projects image report visit
            ReportVisitService._handle_all_projects_visit(user_id, user, date_id, date)
        else:
            # Handle single contract visit
            ReportVisitService._handle_single_contract_visit(
                contract_id, user, date, report_id
            )
        
        return True
    
    @staticmethod
    def _handle_all_projects_visit(user_id, user, date_id, date):
        """Handle report visit for all projects (image report)."""
        report_visits = ReportVisit.objects.filter(
            userid__exact=user_id,
            dateid__exact=date_id
        )
        report_visits.update(imagereport=1)
        
        is_all_project = UserRole.objects.filter(
            userid__exact=user_id,
            contractid__exact=None
        ).count() > 0
        
        if is_all_project:
            contracts = Contract.objects.filter(
                iscompleted__exact=False
            ).exclude(contractid__in=report_visits.values_list('contractid', flat=True))
        else:
            user_contract_roles = UserRole.objects.filter(userid__exact=user_id)
            contracts = Contract.objects.filter(
                contractid__in=user_contract_roles.values_list('contractid', flat=True)
            ).exclude(contractid__in=report_visits.values_list('contractid', flat=True))
        
        for contract in contracts:
            ReportVisit.objects.update_or_create(
                contractid=contract,
                dateid=date,
                userid=user,
                defaults={"imagereport": 1}
            )
    
    @staticmethod
    def _handle_single_contract_visit(contract_id, user, date, report_id):
        """Handle report visit for a single contract."""
        contracts = Contract.objects.filter(contractid__exact=contract_id)
        
        if not contracts.exists():
            return
        
        contract = contracts.first()
        
        # Map report_id to field name
        report_field_map = {
            1: 'financialinfo',
            2: 'hse',
            3: 'progressstate',
            4: 'timeprogressstate',
            5: 'invoice',
            6: 'financialinvoice',
            7: 'workvolume',
            8: 'pmsprogress',
            9: 'budget',
            10: 'machinary',
            11: 'personel',
            12: 'problems',
            13: 'criticalactions',
            14: 'zoneimages',
            15: 'projectdox',
            16: 'durationdox',
            17: 'dashboard_r',
            18: 'dashboard_fc',
            19: 'imagereport',
        }
        
        field_name = report_field_map.get(report_id)
        if field_name is None:
            return
        
        # Create or update report visit
        report_visit, _ = ReportVisit.objects.update_or_create(
            userid=user,
            contractid=contract,
            dateid=date,
            defaults={field_name: 1}
        )
        
        # Create or update visit date record
        ReportVisitdate.objects.update_or_create(
            visitreportid=report_visit,
            reportid=report_id,
            defaults={"visitreportid": report_visit, "reportid": report_id}
        )
    
    @staticmethod
    def create_report_visit(contract_id, date_id, user_id, report_id):
        """
        Create a new report visit record.
        This is the main entry point from the API.
        """
        return ReportVisitService.set_report_visit(
            user_id, contract_id, date_id, report_id
        )