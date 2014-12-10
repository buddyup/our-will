from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class ProductNotificationPlugin(WillPlugin):

    @route("/api/course-added", method="POST")
    def deploy_notification(self):
        assert self.request.json and "course_name" in self.request.json
        payload = self.request.json
        message = rendered_template("course_added.html", context=payload)
        color = "green"
        self.say(message, color=color)

        return "OK"
