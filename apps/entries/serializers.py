from rest_framework import serializers
from .models import MarisInput, MetalInput, BaggingInput


class BaseProductionSerializer(serializers.ModelSerializer):
    shift_display = serializers.CharField(source='get_shift_display', read_only=True)

    class Meta:
        fields = ['id', 'date', 'shift', 'shift_display', 'employee', 'production_data', 'created_at']
        read_only_fields = ['id', 'created_at']


    def validate_production_data(self, value):
        numeric_fields = ['goodPro', 'dlnc', 'scrap', 'reject', 'screenChanger', 'visLab']
        for item in value:
            for field in numeric_fields:
                val = item.get(field)
                try:
                    clean_val = float(val) if val not in [None, ""] else 0.0
                except:
                    clean_val = 0.0
                if clean_val < 0:
                    raise serializers.ValidationError(f"{field} must be positive.")
                item[field] = clean_val
        return value


class MarisInputSerializer(BaseProductionSerializer):
    class Meta(BaseProductionSerializer.Meta):
        model = MarisInput
        fields = BaseProductionSerializer.Meta.fields + [
            'stop_time_data', 'problem_data', 'comment'
        ]


class MetalInputSerializer(BaseProductionSerializer):
    class Meta(BaseProductionSerializer.Meta):
        model = MetalInput
        fields = BaseProductionSerializer.Meta.fields + ['lot_number']


class BaggingInputSerializer(BaseProductionSerializer):
    class Meta(BaseProductionSerializer.Meta):
        model = BaggingInput
        fields = BaseProductionSerializer.Meta.fields + ['employee_2', 'lot_number']
