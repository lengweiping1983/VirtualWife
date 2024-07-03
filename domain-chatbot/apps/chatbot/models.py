from django.db import models


class PortalUser(models.Model):
    '''门户用户基本信息
    '''
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.id


class CustomRoleModel(models.Model):
    '''自定义角色数据结构
        role_name: 角色名称
        persona: 角色基本信息
        personality: 角色的性格简短描述
        scenario: 角色的对话情况和背景
        examples_of_dialogue: 角色的对话样例
        custom_role_template_type: 模版类型
        role_package_id: 角色安装包id
    '''
    id = models.AutoField
    role_name = models.CharField(max_length=100)
    persona = models.TextField()
    personality = models.TextField()
    scenario = models.TextField()
    examples_of_dialogue = models.TextField()
    custom_role_template_type = models.CharField(max_length=100)
    role_package_id = models.IntegerField()

    def __str__(self):
        return self.role_name


class SysConfigModel(models.Model):
    '''系统配置数据结构
        id: 主键id
        code: 配置code
        config: 配置json
    '''
    id = models.AutoField
    code = models.CharField(max_length=100)
    config = models.TextField()

    def __str__(self):
        return self.id


class LocalMemoryModel(models.Model):
    '''记忆数据存储数据结构
        id: 主键id
        user_name: 用户名
        user_text: 用户文本
        role_name: 角色名
        role_text: 角色文本
        timestamp: 创建时间
        automatic: 自动回答（0=否，1=是topic，2=是emotion）
        summary: 生成摘要（0=否，1=是）
        topic: 生成话题（0=否，1=是）
        emotion: 生成情感（0=否，1=是）
        deleted: 已删除（0=否，1=是）
    '''
    id = models.AutoField
    user_name = models.CharField(max_length=100)
    user_text = models.TextField(blank=True, null=True)
    role_name = models.CharField(max_length=100)
    role_text = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField()
    automatic = models.IntegerField()
    summary = models.IntegerField()
    topic = models.IntegerField()
    emotion = models.IntegerField()
    deleted = models.IntegerField()

    def __str__(self):
        return self.id


class BackgroundImageModel(models.Model):
    id = models.AutoField
    original_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='background/')


class VrmModel(models.Model):
    id = models.AutoField
    type = models.CharField(max_length=100)
    original_name = models.CharField(max_length=100)
    vrm = models.FileField(upload_to='vrm/')


class RolePackageModel(models.Model):
    id = models.AutoField
    role_name = models.CharField(max_length=100)
    dataset_json_path = models.CharField(max_length=100)
    embed_index_idx_path = models.CharField(max_length=100)
    system_prompt_txt_path = models.CharField(max_length=100)
    role_package = models.FileField(upload_to='role_package/')
