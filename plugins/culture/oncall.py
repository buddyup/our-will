from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will import settings


ON_CALL_USERS = {
    "mon": "hilliary",
    "tue": "hilliary",
    "wed": "hilliary",
    "thu": "hilliary",
    "fri": "steven",
    "sat": "brian",
    "sun": "steven",
}


class OnCallPlugin(WillPlugin):

    def support_handler(self, day_of_week, user=None, message=None):
        if not user:
            user = ON_CALL_USERS[day_of_week]
        self.say("@%s you're on call for support today!" % user, message=message)
        self.set_topic("Support: @%s | FAQ: http://goo.gl/pX1mhU" % user, message=message)

    # @periodic(hour='8', minute='0', day_of_week="mon")
    # def support_mon(self):
    #     self.support_handler("mon")

    # @periodic(hour='8', minute='0', day_of_week="tue")
    # def support_tue(self):
    #     self.support_handler("tue")

    # @periodic(hour='8', minute='0', day_of_week="wed")
    # def support_wed(self):
    #     self.support_handler("wed")

    # @periodic(hour='8', minute='0', day_of_week="thu")
    # def support_thu(self):
    #     self.support_handler("thu")

    # @periodic(hour='8', minute='0', day_of_week="fri")
    # def support_fri(self):
    #     self.support_handler("fri")

    # @periodic(hour='8', minute='0', day_of_week="sat")
    # def support_sat(self):
    #     self.support_handler("sat")

    # @periodic(hour='8', minute='0', day_of_week="sun")
    # def support_sun(self):
    #     self.support_handler("sun")

    @respond_to("I'm on call")
    def support_today(self, message):
        """I'm on call: sets yourself as the on-call support person for today."""
        self.support_handler("mon", user=message.sender.nick, message=message)
