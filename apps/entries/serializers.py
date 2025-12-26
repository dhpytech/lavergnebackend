from rest_framework import serializers
from .models import MarisInput

from rest_framework import serializers
from .models import MarisInput


class MarisInputSerializer(serializers.ModelSerializer):
    shift_display = serializers.CharField(source='get_shift_display', read_only=True)

    class Meta:
        model = MarisInput
        fields = [
            'id', 'date', 'shift', 'shift_display', 'employee',
            'production_data', 'stop_time_data', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    # noinspection PyMethodMayBeStatic
    def validate_production_data(self, value):
        """
        Validation logic cho mảng JSON sản lượng.
        Đảm bảo Zod và Serializer đồng nhất.
        """
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("At least one production record is required.")

        for item in value:
            if 'productCode' not in item or not item['productCode']:
                raise serializers.ValidationError("Product Code is required for all rows.")
            if 'goodPro' not in item or item['goodPro'] < 0:
                raise serializers.ValidationError("Good Production must be a positive number.")

        return value
