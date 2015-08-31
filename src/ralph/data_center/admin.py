# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from ralph.admin import RalphAdmin, RalphTabularInline, register
from ralph.admin.mixins import BulkEditChangeListMixin
from ralph.admin.views.extra import RalphDetailViewAdmin
from ralph.assets.filters import (
    BarcodeFilter,
    DepreciationDateFilter,
    ForceDepreciationFilter,
    HostnameFilter,
    InvoiceDateFilter,
    InvoiceNoFilter,
    ModelFilter,
    OrderNoFilter,
    RemarksFilter,
    SNFilter,
    StatusFilter
)
from ralph.attachments.admin import AttachmentsMixin
from ralph.data_center.filters import RackFilter
from ralph.data_center.forms.network import NetworkInlineFormset
from ralph.data_center.models.components import DiskShare, DiskShareMount
from ralph.data_center.models.networks import (
    DiscoveryQueue,
    IPAddress,
    Network,
    NetworkEnvironment,
    NetworkKind,
    NetworkTerminator
)
from ralph.data_center.models.physical import (
    Connection,
    DataCenter,
    DataCenterAsset,
    Rack,
    RackAccessory,
    ServerRoom
)
from ralph.data_center.models.virtual import (
    CloudProject,
    Database,
    VIP,
    VirtualServer
)
from ralph.data_center.views.ui import (
    DataCenterAssetComponents,
    DataCenterAssetSecurityInfo,
    DataCenterAssetSoftware
)
from ralph.data_importer import resources
from ralph.lib.permissions.admin import PermissionAdminMixin
from ralph.lib.transitions.admin import TransitionAdminMixin
from ralph.licences.models import BaseObjectLicence


@register(DataCenter)
class DataCenterAdmin(RalphAdmin):

    search_fields = ['name']


class NetworkInline(RalphTabularInline):
    formset = NetworkInlineFormset
    model = IPAddress


class NetworkView(RalphDetailViewAdmin):
    icon = 'chain'
    name = 'network'
    label = 'Network'
    url_name = 'network'

    inlines = [NetworkInline]


class DataCenterAssetSupport(RalphDetailViewAdmin):
    icon = 'bookmark'
    name = 'dc_asset_support'
    label = _('Supports')
    url_name = 'data_center_asset_support'

    class DataCenterAssetSupportInline(RalphTabularInline):
        model = DataCenterAsset.supports.related.through
        raw_id_fields = ('support',)
        extra = 1
        verbose_name = _('Support')

    inlines = [DataCenterAssetSupportInline]


class DataCenterAssetLicence(RalphDetailViewAdmin):
    icon = 'key'
    name = 'dc_asset_licences'
    label = _('Licences')
    url_name = 'data_center_asset_licences'

    class DataCenterAssetLicenceInline(RalphTabularInline):
        model = BaseObjectLicence
        raw_id_fields = ('licence',)
        extra = 1

    inlines = [DataCenterAssetLicenceInline]


@register(DataCenterAsset)
class DataCenterAssetAdmin(
    TransitionAdminMixin,
    BulkEditChangeListMixin,
    PermissionAdminMixin,
    AttachmentsMixin,
    RalphAdmin,
):
    """Data Center Asset admin class."""
    actions = ['bulk_edit_action']
    change_views = [
        DataCenterAssetComponents,
        DataCenterAssetSoftware,
        DataCenterAssetSecurityInfo,
        DataCenterAssetLicence,
        DataCenterAssetSupport,
        NetworkView,
    ]
    resource_class = resources.DataCenterAssetResource
    list_display = [
        'status', 'barcode', 'model',
        'sn', 'hostname', 'invoice_date', 'invoice_no',
    ]
    bulk_edit_list = list_display
    search_fields = ['barcode', 'sn', 'hostname', 'invoice_no', 'order_no']
    list_filter = [
        StatusFilter, BarcodeFilter, SNFilter, HostnameFilter, InvoiceNoFilter,
        InvoiceDateFilter, OrderNoFilter, ModelFilter, DepreciationDateFilter,
        ForceDepreciationFilter, RemarksFilter, RackFilter
    ]
    date_hierarchy = 'created'
    list_select_related = ['model', 'model__manufacturer']
    raw_id_fields = ['model', 'rack', 'service_env', 'parent']
    raw_id_override_parent = {'parent': DataCenterAsset}

    fieldsets = (
        (_('Basic info'), {
            'fields': (
                'hostname', 'model', 'status', 'barcode', 'sn', 'niw',
                'required_support', 'remarks', 'parent',
            )
        }),
        (_('Location Info'), {
            'fields': (
                'rack', 'position', 'orientation', 'slot_no',
            )
        }),
        (_('Usage info'), {
            'fields': (
                'service_env', 'configuration_path', 'production_year',
                'production_use_date',
            )
        }),
        (_('Financial & Order Info'), {
            'fields': (
                'order_no', 'invoice_date', 'invoice_no', 'task_url', 'price',
                'depreciation_rate', 'depreciation_end_date',
                'force_depreciation', 'source', 'provider', 'delivery_date',

            )
        }),
    )


@register(ServerRoom)
class ServerRoomAdmin(RalphAdmin):

    list_select_related = ['data_center']
    search_fields = ['name', 'data_center__name']
    resource_class = resources.ServerRoomResource


class RackAccessoryInline(RalphTabularInline):
    model = RackAccessory


@register(Rack)
class RackAdmin(RalphAdmin):

    exclude = ['accessories']
    list_display = ['name', 'server_room']
    list_filter = ['server_room__data_center']
    list_select_related = ['server_room', 'server_room__data_center']
    search_fields = ['name']
    inlines = [RackAccessoryInline]
    resource_class = resources.RackResource

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "server_room":
            kwargs["queryset"] = ServerRoom.objects.select_related(
                'data_center',
            )
        return super(RackAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )


@register(RackAccessory)
class RackAccessoryAdmin(RalphAdmin):

    list_select_related = ['rack', 'accessory']
    search_fields = ['accessory__name', 'rack__name']
    raw_id_fields = ['rack']
    resource_class = resources.RackAccessoryResource


@register(Database)
class DatabaseAdmin(RalphAdmin):
    pass


@register(VIP)
class VIPAdmin(RalphAdmin):
    pass


@register(VirtualServer)
class VirtualServerAdmin(RalphAdmin):
    pass


@register(CloudProject)
class CloudProjectAdmin(RalphAdmin):
    pass


@register(Connection)
class ConnectionAdmin(RalphAdmin):

    resource_class = resources.ConnectionResource


@register(DiskShare)
class DiskShareAdmin(RalphAdmin):
    pass


@register(DiskShareMount)
class DiskShareMountAdmin(RalphAdmin):
    pass


@register(Network)
class NetworkAdmin(RalphAdmin):

    resource_class = resources.NetworkResource


@register(NetworkEnvironment)
class NetworkEnvironmentAdmin(RalphAdmin):
    pass


@register(NetworkKind)
class NetworkKindAdmin(RalphAdmin):
    pass


@register(NetworkTerminator)
class NetworkTerminatorAdmin(RalphAdmin):
    pass


@register(DiscoveryQueue)
class DiscoveryQueueAdmin(RalphAdmin):
    pass


@register(IPAddress)
class IPAddressAdmin(RalphAdmin):

    search_fields = ['address']
    list_filter = ['is_public', 'is_management']
    list_display = ['address', 'asset', 'is_public']
    list_select_related = ['asset']
    raw_id_fields = ['asset']
    resource_class = resources.IPAddressResource
