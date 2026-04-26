from .common_aggregate_services import BaseProductionAggregateService
from ..models import BaggingInput


class BaggingAggregateService (BaseProductionAggregateService):
    model_class = BaggingInput
