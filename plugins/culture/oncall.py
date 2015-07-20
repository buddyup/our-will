from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will import settings


ON_CALL_USERS = {
    "mon": "hilliary",
    "tue": "brian",
    "wed": "hilliary",
    "thu": "brian",
    "fri": "steven",
    "sat": "brian",
    "sun": "steven",
}


class OnCallPlugin(WillPlugin):

    def support_handler(self, day_of_week):
        user = ON_CALL_USERS[day_of_week]
        self.say("@%s you're on call for support today!" % user)
        self.set_topic("Support: @%s | FAQ: http://goo.gl/pX1mhU" % user)

    @periodic(hour='8', minute='0', day_of_week="mon")
    def support_mon(self):
        self.support_handler("mon")

    @periodic(hour='8', minute='0', day_of_week="tue")
    def support_tue(self):
        self.support_handler("tue")

    @periodic(hour='8', minute='0', day_of_week="wed")
    def support_wed(self):
        self.support_handler("wed")

    @periodic(hour='8', minute='0', day_of_week="thu")
    def support_thu(self):
        self.support_handler("thu")

    @periodic(hour='8', minute='0', day_of_week="fri")
    def support_fri(self):
        self.support_handler("fri")

    @periodic(hour='8', minute='0', day_of_week="sat")
    def support_sat(self):
        self.support_handler("sat")

    @periodic(hour='8', minute='0', day_of_week="sun")
    def support_sun(self):
        self.support_handler("sun")
