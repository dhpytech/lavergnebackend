from ..models import MetalInput
from .common_aggregate_services import BaseProductionAggregateService


class MetalAggregateService(BaseProductionAggregateService):
    model_class = MetalInput
