import logging

from ..models import PortalUser
from ..utils import singleton_snow_flake
from ..utils.json_utils import read_json, dumps_json


logger = logging.getLogger(__name__)


class PortalUserService:

    def get_by_user_name(self, user_name: str) -> PortalUser:
        portalUser = PortalUser.objects.filter(user_name=user_name).last()
        if portalUser is None:
            return self.save_by_user_name(user_name=user_name)
        return portalUser

    def save_by_user_name(self, user_name: str) -> PortalUser:
        portalUser = PortalUser(
            id=singleton_snow_flake.task(),
            user_name=user_name
            )
        return self.save(portalUser)
    
    def save(self, portalUser: PortalUser) -> PortalUser:
        if portalUser is None:
            return
        if portalUser.user_name is None or portalUser.user_name == "":
            return
        if portalUser.id is None:
            portalUser.id = singleton_snow_flake.task()
        if portalUser.portrait is None:
            portrait = {
                            "portrait": {
                                "Persona": "未知",
                                "Fictional name": portalUser.user_name,
                                "Sex": "未知",
                                "Job title/major responsibilities": "未知",
                                "Demographics": "未知",
                                "Goals and tasks": "未知",
                                "Hobby": "未知",
                                "Promise": "未知",
                                "Topic": "未知"
                            }
                        }
            portalUser.portrait = dumps_json(portrait)
        portalUser.save()
        return portalUser
