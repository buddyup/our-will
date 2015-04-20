from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class FunImagesPlugin(WillPlugin):

    @hear("high(-| )(5|five)")
    def hear_highfive(self, message):
        """high 5: Will's got spirit."""
        self.say("https://buddyup-will.s3.amazonaws.com/highfive.jpg", message=message)

    @hear("(money|dollars?)")
    def hear_money(self, message):
        """money: make it rain."""
        self.say("https://s3.amazonaws.com/uploads.hipchat.com/183747/1970469/ymR4Tivk6jwgRH7/Kenny-Powers-Dolla.gif", message=message)
