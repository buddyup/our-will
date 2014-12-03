from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class SalesCyclePlugin(WillPlugin):

    @route("/api/sales-update", method="POST")
    def deploy_notification(self):
        assert self.request.json and "name" in self.request.json
        payload = self.request.json
        message = rendered_template("sales_update.html", context=payload)
        color = "green"
        self.say(message, html=True, color=color)
        self.say("(boom)", color=color)

        return "OK"
