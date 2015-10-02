from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings


class ProductNotificationPlugin(WillPlugin):

    @route("/api/signup", method="POST")
    def new_signup(self):
        assert self.request.json and "email" in self.request.json
        payload = self.request.json
        message = rendered_template("new_user.html", context=payload)
        color = "green"
        self.say(message, color=color)

        return "OK"

    @route("/api/group", method="POST")
    def new_group(self):
        assert self.request.json and "email" in self.request.json
        payload = self.request.json
        print(payload)
        message = rendered_template("new_group.html", context=payload)
        color = "green"
        self.say(message, color=color)

        return "OK"

    @route("/api/class", method="POST")
    def new_course(self):
        assert self.request.json and "email" in self.request.json
        payload = self.request.json
        message = rendered_template("new_course.html", context=payload)
        color = "green"
        self.say(message, color=color)

        return "OK"

    @route("/api/reported", method="POST")
    def reported_content(self):
        print self.request
        print self.request.json
        assert self.request.json is not None
        payload = self.request.json
        # message = rendered_template("new_user.html", context=payload)
        color = "red"
        self.say("@all Reported content!", color=color)
        self.say("Raw dump:", color=color)
        self.say("/code %s" % payload)

        return "OK"


    @route("/api/cancel-report", method="POST")
    def reported_content(self):
        assert self.request.json is not None
        payload = self.request.json
        # message = rendered_template("new_user.html", context=payload)
        color = "red"
        self.say("@all Reported content!", color=color)
        self.say("Raw dump:", color=color)
        self.say("/code %s" % payload)

        return "OK"

    @route("/api/course-added", method="POST")
    def course_added(self):
        assert self.request.json and "course_name" in self.request.json
        payload = self.request.json
        message = rendered_template("course_added.html", context=payload)
        color = "green"
        self.say(message, color=color)

        return "OK"

    @route("/api/event-added", method="POST")
    def event_added(self):
        assert self.request.json and "event_name" in self.request.json
        payload = self.request.json
        message = rendered_template("event_added.html", context=payload)
        color = "green"
        self.say(message, color=color)

        return "OK"

    @route("/api/tutor-application", method="POST")
    def tutor_application(self):
        assert self.request.json and "user_name" in self.request.json
        payload = self.request.json
        message = rendered_template("tutor_application.html", context=payload)
        color = "green"
        self.say(message, color=color)

        return "OK"
