from ..models import CustomRoleModel
from .character import Character
from .default_character import character_list
from .base_character_template import BaseCharacterTemplate
from .character_template_zh import ChineseCharacterTemplate


class CharacterGeneration():
    character_template_dict: dict[str, BaseCharacterTemplate] = {}

    def __init__(self) -> None:
        # 加载模型
        self.character_template_dict["zh"] = ChineseCharacterTemplate()

    def get_character(self, role_id: int) -> Character:
        '''获取自定义角色对象'''
        character_model = CustomRoleModel.objects.filter(pk=role_id).first()
        if character_model is not None:
            character = Character(
                role_id=character_model.id,
                role_name=character_model.role_name,
                persona=character_model.persona,
                personality=character_model.personality,
                scenario=character_model.scenario,
                examples_of_dialogue=character_model.examples_of_dialogue,
                custom_role_template_type=character_model.custom_role_template_type,
                role_package_id=character_model.role_package_id
            )
        if character is None:
            character = character_list[0]
        return character

    def output_prompt(self, character: Character) -> str:
        '''获取角色prompt'''
        character_template = self.character_template_dict[
            character.custom_role_template_type]
        return character_template.format(character)


singleton_character_generation = CharacterGeneration()
