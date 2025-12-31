from rest_framework import serializers
from .models import MarisInput, MetalInput, BaggingInput

class BaseProductionSerializer(serializers.ModelSerializer):
    shift_display = serializers.CharField(source='get_shift_display', read_only=True)

    class Meta:
        # Chúng ta không gán model ở đây vì đây là lớp trừu tượng cho Serializer
        fields = ['id', 'date', 'shift', 'shift_display', 'employee', 'production_data', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_production_data(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("At least one production record is required.")

        for item in value:
            if 'productCode' not in item or not item['productCode']:
                raise serializers.ValidationError("Product Code is required for all rows.")
            # Sử dụng get() để tránh lỗi KeyError nếu FE gửi thiếu field
            if float(item.get('goodPro', 0)) < 0:
                raise serializers.ValidationError("Quantity must be a positive number.")
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
