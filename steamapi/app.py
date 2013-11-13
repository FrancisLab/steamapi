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
    def app_info(self):
        response = StoreAPIConnection().call("appdetails", appids=self._id, filters="basic,fullgame,developers," +
                                                                                    "publishers,demos,price_overview," +
                                                                                    "platforms,metacritic,categories," +
                                                                                    "genres,recommendations," +
                                                                                    "release_date")
        if response[str(self._id)].success:
            return response[str(self._id)].data

    @property
    def name(self):
        if self.app_info:
            #Names returned by StoreFrontApi are in UTF-8
            return self.app_info.name.encode('ascii', 'ignore')

    @property
    def type(self):
        """ Either 'game', 'movie' or 'demo'. More values could be possible.  """
        if self.app_info:
            return self.app_info.type

    @property
    def required_age(self):
        """ Minimum age to access SteamApp. """
        if self.app_info:
            return self.app_info.required_age

    @property
    def dlc(self):
        """ List the appids of the SteamApp's DLCs. """
        if self.app_info and self.app_info.dlc:
            return [SteamApp(app_id) for app_id in self.app_info.dlc]
        else:
            return []

    @property
    def detailed_description(self):
        """ Detailed unicode description of SteamApp in html. """
        if self.app_info:
            return self.app_info.detailed_description

    @property
    def about_the_game(self):
        """ Short unicode description of SteamApp in html. """
        if self.app_info:
            return self.app_info.about_the_game

    @cached_property(ttl=INFINITE)
    def supported_languages(self):
        """
        Returns information concerning languages supported by the SteamApp.
            full_audio_support: List of languages providing full audio support.
            basic_support: List of languages providing only interface translation and subtitles.
        """
        if self.app_info and self.app_info.supported_languages:
            languages_string = self.app_info.supported_languages
            languages_string = languages_string[:languages_string.find("<br>")]
            languages = languages_string.split(",")

            full_audio_support = [lang[:lang.find('<')] for lang in languages if lang.find('*') != -1]
            basic_support = full_audio_support + [lang for lang in languages if lang.find('*') == -1]

            return {'full_audio_support': full_audio_support, 'basic_support': basic_support}

    @property
    def header_image(self):
        """ Link to the header image of the SteamApp. """
        if self.app_info:
            return self.app_info.header_image

    @property
    def legal_notice(self):
        """ Legal notice attached to the SteamApp. """
        if self.app_info:
            return self.app_info.legal_notice

    @property
    def website(self):
        """ Link to the SteamApp's website. """
        if self.app_info:
            return self.app_info.website

    @property
    def pc_requirements(self):
        """
        Dictionary describing PC requirements to run SteamApp.
            recommended: Html string describing recommended requirements
            minimunm: Html string describing minimal requirements
        """
        if self.app_info and self.app_info.pc_requirements:
            return self.app_info.pc_requirements
        else:
            return {'recommended': '', 'minimum': ''}


    @property
    def mac_requirements(self):
        """
        Dictionary describing Mac requirements to run SteamApp.
            recommended: Html string describing recommended requirements
            minimunm: Html string describing minimal requirements
        """
        if self.app_info and self.app_info.mac_requirements:
            return self.app_info.mac_requirements
        else:
            return {'recommended': '', 'minimum': ''}

    @property
    def linux_requirements(self):
        """
        Dictionary describing linux requirements to run SteamApp.
            recommended: Html string describing recommended requirements
            minimunm: Html string describing minimal requirements
        """
        if self.app_info and self.app_info.linux_requirements:
            return self.app_info.linux_requirements
        else:
            return {'recommended': '', 'minimum': ''}

    @property
    def fullgame(self):
        """ Steam id of fullgame if current SteamApp is a demo. """
        if self.app_info and self.app_info.fullgame:
            return SteamApp(self.app_info.fullgame.appid)

    @property
    def developers(self):
        """ List of SteamApp's developers. """
        if self.app_info:
            return self.app_info.developers

    @property
    def publishers(self):
        """ List of SteamApp's publishers. """
        if self.app_info:
            return self.app_info.publishers

    @cached_property(ttl=INFINITE)
    def demos(self):
        """
        Information about the SteamApp's demo. None if there is none.
            demos: List of demo SteamApps of the current SteamApp
            description: Used to note the demo's restrictions
        """
        if self.app_info and self.app_info.demos:
            return [{'demo': SteamApp(demo.appid), 'description': demo.description} for demo in self.app_info.demos]
        else:
            return []

    @property
    def price_overview(self):
        """
        Information about the SteamApp's demo. None if free-to-play.
            currency: Currency prices are noted in.
            initial: Pre-discount price
            final: Discounted price
            discount_percent
        """
        if self.app_info:
            return self.app_info.price_overview

    @property
    def platforms(self):
        """
        Booleans indicating whether SteamApp is available on platform.
            windows
            mac
            linux
        """
        if self.app_info:
            return self.app_info.platforms

    @property
    def metacritic(self):
        """
        Information about SteamApp's metacritic score. None if there is no score.
            score
            url: Url to metacritic page.
        """
        if self.app_info:
            return self.app_info.metacritic

    @cached_property(ttl=INFINITE)
    def categories(self):
        """
        List of the categories the SteamApp belongs to.
            id: An integer associated with the category
            description: Short description of the category
        """
        if self.app_info and self.app_info.categories:
            return [category.description for category in self.app_info.categories]
        else:
            return []

    @cached_property(ttl=INFINITE)
    def genres(self):
        """
        List of the categories the SteamApp belongs to.
            id: An integer associated with the genre
            description: Short description of the genre
        """
        if self.app_info and self.app_info.genres:
            return [genre.description for genre in self.app_info.genres]
        else:
            return []

    @property
    def recommendations(self):
        """
        Information related to the SteamApp recommendations
            total : integer
        """
        if self.app_info:
            return self.app_info.recommendations

    @property
    def release_date(self):
        """
        Information related to the SteamApp's release date.
            coming_soon: True if unreleased, False otherwise
            date: Date string formatted according to cc parameter. Empty when unreleased.
        """
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