from rest_framework import serializers
from .models import File, Folder


class FileSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', read_only=True
    )
    modified = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', read_only=True
    )
    file = serializers.FileField(write_only=True)

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        validated_data['initialization_vector'] = \
            self.context['request'].FILES['file'].initialization_vector
        validated_data['cipher_key'] = \
            self.context['request'].FILES['file'].cipher_key

        return super().create(validated_data)

    class Meta:
        model = File
        fields = '__all__'
        read_only_fields = ('owner', )


class FolderSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = Folder
        fields = '__all__'
        read_only_fields = ('owner', )


class DirectoryChildSerializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.CharField()
    type = serializers.CharField()
    created = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', read_only=True
    )
    modified = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M:%S', read_only=True
    )

    class Meta:
        fields = '__all__'


class DirectorySerializer(serializers.Serializer):
    id = serializers.CharField()
    parent = serializers.ReadOnlyField(source='parent.id')
    path = serializers.CharField()
    children = DirectoryChildSerializer(many=True)

    class Meta:
        fields = '__all__'
