from rest_framework import serializers
from apps.system.models import User, Role, Menu, Department


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器：包含部门名称、角色列表、关联员工信息
    """
    dept_name = serializers.CharField(source='dept.name', read_only=True)
    role_names = serializers.SerializerMethodField(read_only=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        source='roles', many=True, queryset=Role.objects.all(), required=False
    )
    employee_id = serializers.IntegerField(source='employee_profile.id', read_only=True)
    employee_name = serializers.CharField(source='employee_profile.name', read_only=True)
    employee_no = serializers.CharField(source='employee_profile.employee_no', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'avatar',
            'dept', 'dept_name', 'role_ids', 'role_names',
            'is_active', 'is_superuser', 'created_at', 'updated_at', 'password',
            'employee_id', 'employee_name', 'employee_no',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def get_role_names(self, obj):
        return [role.name for role in obj.roles.all()]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        roles = validated_data.pop('roles', [])
        user = super().create(validated_data)
        if password is not None:
            user.set_password(password)
        if roles:
            user.roles.set(roles)
        if password is not None or roles:
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        roles = validated_data.pop('roles', None)
        user = super().update(instance, validated_data)
        if password is not None:
            user.set_password(password)
            user.save()
        if roles is not None:
            user.roles.set(roles)
        return user


class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化器
    """
    menu_ids = serializers.PrimaryKeyRelatedField(
        source='menus', many=True, queryset=Menu.objects.all(), required=False
    )

    class Meta:
        model = Role
        fields = '__all__'

    def create(self, validated_data):
        menus = validated_data.pop('menus', [])
        role = super().create(validated_data)
        if menus:
            role.menus.set(menus)
        return role

    def update(self, instance, validated_data):
        menus = validated_data.pop('menus', None)
        role = super().update(instance, validated_data)
        if menus is not None:
            role.menus.set(menus)
        return role


class MenuSerializer(serializers.ModelSerializer):
    """
    菜单序列化器
    """
    children = serializers.SerializerMethodField(read_only=True)
    parent_name = serializers.CharField(source='parent.title', read_only=True)

    class Meta:
        model = Menu
        fields = '__all__'

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        if children.exists():
            return MenuSerializer(children, many=True, context=self.context).data
        return []

    def validate(self, data):
        menu_type = data.get('menu_type', self.instance.menu_type if self.instance else 'MENU')
        path = data.get('path')
        component = data.get('component')
        permission = data.get('permission')

        if menu_type == 'MENU':
            if not path or not path.strip():
                raise serializers.ValidationError({'path': '菜单类型的路由路径不能为空'})
            if not component or not component.strip():
                raise serializers.ValidationError({'component': '菜单类型的组件路径不能为空'})
        elif menu_type == 'BUTTON':
            if not permission or not permission.strip():
                raise serializers.ValidationError({'permission': '按钮类型的权限标识不能为空'})

        return data

    def validate_parent(self, value):
        if self.instance and value:
            if value.id == self.instance.id:
                raise serializers.ValidationError('上级菜单不能选择自己')
            # 检查是否选择了自己的后代节点
            parent = value.parent
            while parent:
                if parent.id == self.instance.id:
                    raise serializers.ValidationError('上级菜单不能选择自己的子菜单')
                parent = parent.parent
        return value


class DepartmentSerializer(serializers.ModelSerializer):
    """
    部门序列化器
    """
    children = serializers.SerializerMethodField(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    user_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Department
        fields = '__all__'

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        if children.exists():
            return DepartmentSerializer(children, many=True, context=self.context).data
        return []

    def get_user_count(self, obj):
        return self._count_users(obj)

    def _count_users(self, dept):
        count = dept.user_set.filter(is_active=True).count()
        for child in dept.children.filter(is_active=True):
            count += self._count_users(child)
        return count

    def validate_parent(self, value):
        if self.instance and value:
            if value.id == self.instance.id:
                raise serializers.ValidationError('上级部门不能选择自己')
            parent = value.parent
            while parent:
                if parent.id == self.instance.id:
                    raise serializers.ValidationError('上级部门不能选择自己的子部门')
                parent = parent.parent
        return value
