__author__ = 'SmileyBarry'

from .core import APIConnection, SteamObject, StoreAPIConnection
from .decorators import cached_property, INFINITE


class SteamApp(SteamObject):
    def __init__(self, appid, name=None):
        self._id = appid
        if name is not None:
            import time
            self._cache = dict()
            self._cache['name'] = (name, time.time())

    @property
    def appid(self):
        return self._id

    @cached_property(ttl=INFINITE)
    def achievements(self):
        response = APIConnection().call("ISteamUserStats", "GetSchemaForGame", "v2", appid=self._id)
        achievements_list = []
        import time
        for achievement in response.game.availableGameStats.achievements:
            achievement_obj = SteamAchievement(self._id, achievement.name, achievement.displayName)
            achievement_obj._cache = {}
            if achievement.hidden == 0:
                achievement_obj._cache['hidden'] = (False, time.time())
            else:
                achievement_obj._cache['hidden'] = (True, time.time())
            achievements_list += [achievement_obj]
        return achievements_list

    @cached_property(ttl=INFINITE)
    def name(self):
        response = APIConnection().call("ISteamUserStats", "GetSchemaForGame", "v2", appid=self._id)
        return response.game.gameName

    @cached_property(ttl=INFINITE)
    def type(self):
        response = StoreAPIConnection().call("appdetails", appids=self._id, filters="basic")
        return response[str(self._id)].data.type

    @cached_property(ttl=INFINITE)
    def required_age(self):
        response = StoreAPIConnection().call("appdetails", appids=self._id, filters="basic")
        return response[str(self._id)].data.required_age

    @cached_property(ttl=INFINITE)
    def dlc(self):
        response = StoreAPIConnection().call("appdetails", appids=self._id, filters="basic")
        return response[str(self._id)].data.dlc

    @cached_property(ttl=INFINITE)
    def detailed_description(self):
        response = StoreAPIConnection().call("appdetails", appids=self._id, filters="basic")
        return response[str(self._id)].data.detailed_description

    @cached_property(ttl=INFINITE)
    def about_the_game(self):
        response = StoreAPIConnection().call("appdetails", appids=self._id, filters="basic")
        return response[str(self._id)].data.about_the_game

    @cached_property(ttl=INFINITE)
    def supported_languages(self):
        response = StoreAPIConnection().call("appdetails", appids=self._id, filters="basic")
        return response[str(self._id)].data.supported_languages

    @cached_property(ttl=INFINITE)
    def header_image(self):
        response = StoreAPIConnection().call("appdetails", appids=self._id, filters="basic")
        return response[str(self._id)].data.header_image

    @cached_property(ttl=INFINITE)
    def website(self):
        response = StoreAPIConnection().call("appdetails", appids=self._id, filters="basic")
        return response[str(self._id)].data.website

    @cached_property(ttl=INFINITE)
    def pc_requirements(self):
        response = StoreAPIConnection().call("appdetails", appids=self._id, filters="basic")
        return response[str(self._id)].data.pc_requirements

    @cached_property(ttl=INFINITE)
    def mac_requirements(self):
        response = StoreAPIConnection().call("appdetails", appids=self._id, filters="basic")
        return response[str(self._id)].data.mac_requirements

    @cached_property(ttl=INFINITE)
    def linux_requirements(self):
        response = StoreAPIConnection().call("appdetails", appids=self._id, filters="basic")
        return response[str(self._id)].data.linux_requirements

    def __str__(self):
        return self.name


class SteamAchievement(SteamObject):
    def __init__(self, linked_appid, apiname, displayname, linked_userid=None):
        self._appid = linked_appid
        self._id = apiname
        self._displayname = displayname
        self._userid = linked_userid

    @property
    def appid(self):
        return self._appid

    @property
    def name(self):
        return self._displayname

    @property
    def apiname(self):
        return self._id

    @property
    def id(self):
        return self._id

    @cached_property(ttl=INFINITE)
    def is_hidden(self):
        response = APIConnection().call("ISteamUserStats",
                                        "GetSchemaForGame",
                                        "v2",
                                        appid=self._appid)
        for achievement in response.game.availableGameStats.achievements:
            if achievement.name == self._id:
                if achievement.hidden == 0:
                    return False
                else:
                    return True

    @cached_property(ttl=INFINITE)
    def is_achieved(self):
        if self._userid is None:
            raise ValueError("No Steam ID linked to this achievement!")
        response = APIConnection().call("ISteamUserStats",
                                        "GetPlayerAchievements",
                                        "v1",
                                        steamid=self._userid,
                                        appid=self._appid,
                                        l="English")
        for achievement in response.playerstats.achievements:
            if achievement.apiname == self._id:
                if achievement.achieved == 1:
                    return True
                else:
                    return False
        # Cannot be found.
        return False