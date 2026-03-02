class HookableSerializerMixin:
    """
    REQUIRED mixin for serializers used with ApiViewSet.

    Bridges DRF's serializer.save() flow with ApiViewSet lifecycle hooks.
    Without this mixin, create_after_init, create_after_save, update_after_assign,
    and update_after_save hooks will NOT be called.

    Usage:
        class MySerializer(HookableSerializerMixin, serializers.ModelSerializer):
            class Meta:
                model = MyModel
                fields = [...]
    """

    def _extract_m2m_fields(self, validated_data):
        """Pop M2M fields from validated_data and return them separately."""
        m2m_names = {f.name for f in self.Meta.model._meta.many_to_many}
        m2m_fields = {}
        for field_name in list(validated_data):
            if field_name in m2m_names:
                m2m_fields[field_name] = validated_data.pop(field_name)
        return m2m_fields

    def create(self, validated_data):
        view = self.context.get("view")
        ModelClass = self.Meta.model  # noqa: N806

        m2m_fields = self._extract_m2m_fields(validated_data)

        instance = ModelClass(**validated_data)

        if view and hasattr(view, "create_after_init"):
            view.create_after_init(instance)

        try:
            instance.full_clean()
            instance.save()
            for field_name, value in m2m_fields.items():
                getattr(instance, field_name).set(value)
            success = True
        except Exception:
            success = False
            if view and hasattr(view, "create_after_save"):
                view.create_after_save(instance, False)
            raise

        if view and hasattr(view, "create_after_save"):
            view.create_after_save(instance, success)

        return instance

    def update(self, instance, validated_data):
        view = self.context.get("view")

        m2m_fields = self._extract_m2m_fields(validated_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if view and hasattr(view, "update_after_assign"):
            view.update_after_assign(instance)

        try:
            instance.full_clean()
            instance.save()
            for field_name, value in m2m_fields.items():
                getattr(instance, field_name).set(value)
            success = True
        except Exception:
            success = False
            if view and hasattr(view, "update_after_save"):
                view.update_after_save(instance, False)
            raise

        if view and hasattr(view, "update_after_save"):
            view.update_after_save(instance, success)

        return instance
