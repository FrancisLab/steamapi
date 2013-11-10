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
    def app_info(self):
        response = StoreAPIConnection().call("appdetails", appids=self._id, filters="basic,fullgame,developers," +
                                                                                    "publishers,demos,price_overview," +
                                                                                    "platforms,metacritic,categories," +
                                                                                    "genres,recommendations," +
                                                                                    "release_date")
        if response[str(self._id)].success:
            return response[str(self._id)].data

    @property
    def type(self):
        if self.app_info:
            return self.app_info.type

    @property
    def required_age(self):
        if self.app_info:
            return self.app_info.required_age

    @property
    def dlc(self):
        if self.app_info:
            return self.app_info.dlc

    @property
    def detailed_description(self):
        if self.app_info:
            return self.app_info.detailed_description

    @property
    def about_the_game(self):
        if self.app_info:
            return self.app_info.about_the_game

    @property
    def supported_languages(self):
        if self.app_info:
            return self.app_info.supported_languages

    @property
    def header_image(self):
        if self.app_info:
            return self.app_info.header_image

    @property
    def website(self):
        if self.app_info:
            return self.app_info.website

    @property
    def pc_requirements(self):
        if self.app_info:
            return self.app_info.pc_requirements

    @property
    def mac_requirements(self):
        if self.app_info:
            return self.app_info.mac_requirements

    @property
    def linux_requirements(self):
        if self.app_info:
            return self.app_info.linux_requirements

    @property
    def fullgame(self):
        if self.app_info:
            return self.app_info.fullgame

    @property
    def developers(self):
        if self.app_info:
            return self.app_info.developers

    @property
    def publishers(self):
        if self.app_info:
            return self.app_info.publishers

    @property
    def demos(self):
        if self.app_info:
            return self.app_info.demos

    @property
    def price_overview(self):
        if self.app_info:
            return self.app_info.price_overview

    @property
    def platforms(self):
        if self.app_info:
            return self.app_info.platforms

    @property
    def metacritic(self):
        if self.app_info:
            return self.app_info.metacritic

    @property
    def categories(self):
        if self.app_info:
            return self.app_info.categories

    @property
    def genres(self):
        if self.app_info:
            return self.app_info.genres

    @property
    def recommendations(self):
        if self.app_info:
            return self.app_info.recommendations

    @property
    def release_date(self):
        if self.app_info:
            return self.app_info.release_date

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