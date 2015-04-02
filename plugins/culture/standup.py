from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will import settings

class StandupPlugin(WillPlugin):

    @periodic(hour='8', minute='45', day_of_week="mon-fri")
    @require_settings("ZOOM_URL")
    def standup(self):
        self.say("@here Standup! %s" % settings.ZOOM_URL)
