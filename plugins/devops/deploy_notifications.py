from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings

SITE_BRANCH_MAPPINGS = {
    "buddyup": "http://pdx.buddyup.org",
    "our-will": "http://will.buddyup.org",
}


class DeployedPlugin(WillPlugin):

    @route("/api/circleci/deployed/", method="POST")
    def deploy_notification(self):
        # Options: https://circleci.com/docs/api#build
        assert self.request.json and "payload" in self.request.json
        payload = self.request.json["payload"]
        if "branch" in payload and payload["branch"] == "master":
            payload["project_name"] = payload["reponame"].title()
            payload["project_url"] = None
            if payload["reponame"] in SITE_BRANCH_MAPPINGS:
                payload["project_url"] = SITE_BRANCH_MAPPINGS[payload["reponame"]]
            message = rendered_template("deploy_notification.html", context=payload)
            color = "green"
            if payload["outcome"] != "success":
                color = "red"
            self.say(message, html=True, color=color)

        return "OK"

    @route("/api/ionic/deployed/", method="POST")
    def ionic_deploy_notification(self):
        self.say("@all new build available in ionic app!", color="green")
        return "OK"

    @route("/api/docker/build/", method="POST")
    def docker_build_notification(self):
        # https://hub.docker.com/r/buddyup/core/~/settings/webhooks/
        data = self.request.json["repository"]
        self.say("@here new docker build of %s is ready!" % data["name"], color="green")
        return "OK"
