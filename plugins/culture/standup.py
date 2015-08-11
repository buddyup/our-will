from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will import settings


class StandupPlugin(WillPlugin):

    @periodic(hour='9', minute='30', day_of_week="mon-fri")
    @require_settings("ZOOM_URL")
    def standup(self):
        self.say("@here Standup! %s" % settings.ZOOM_URL)
        self.say("Launch plan: https://groundcontrol.buddyup.org/#/app/launch_list")
