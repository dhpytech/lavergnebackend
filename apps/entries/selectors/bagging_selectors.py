from ..models import BaggingInput
from .common_selectors import get_entries_selector


def get_bagging_entries_selector(**kwargs):
    return get_entries_selector(BaggingInput, **kwargs)