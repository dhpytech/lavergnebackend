from ..models import MetalInput
from .common_selectors import get_entries_selector


def get_metal_entries_selector(**kwargs):
    return get_entries_selector(MetalInput, **kwargs)
