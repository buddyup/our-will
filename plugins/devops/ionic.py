from will.plugin import WillPlugin
from will.decorators import respond_to


class IonicPlugin(WillPlugin):

    @respond_to("^(qr|ionic)")
    def send_qr_image(self, message):
        # self.say(
            # "https://s3.amazonaws.com/uploads.hipchat.com/183747/1321383/75jBtlWrcnnmHea/upload.png",
            # message=message
        # )
        self.say("App id is:", message=message)
        self.say("/code 0de1e300", message=message)
