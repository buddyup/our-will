from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class FunImagesPlugin(WillPlugin):

    @hear("high(-| )(5|five)")
    def hear_highfive(self, message):
        """high 5: Will's got spirit."""
        self.say("https://buddyup-will.s3.amazonaws.com/highfive.jpg", message=message)
