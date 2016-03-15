"""Pipedrive CRM Plugin for Will."""

from will.plugin import WillPlugin
from will.decorators import (
    periodic,
    rendered_template,
    route,
)


class PipedrivePlugin(WillPlugin):
    """A Will plugin for BuddyUp's CRM Pipedrive's webhooks."""

    def _pipedrive_deal_stage_changed(self, payload):
        return payload['current']['stage_id'] != payload['previous']['stage_id']

    @route("/api/pipedrive-update", method="POST")
    def pipedrive_notification(self):
        """Web hook push notification endpoint from Pipedrive subscription(s) when a deal moves.

        https://developers.pipedrive.com/v1#methods-PushNotifications / REST Hooks / Web hooks
        """
        print self.request.json
        assert self.request.json and "current" in self.request.json and "previous" in self.request.json
        pipedrive_users = self.load('pipedrive_users') or {}
        body = self.request.json

        if not self._pipedrive_deal_stage_changed(body):
            return 'OK'

        payload = {
            'name': pipedrive_users.get(body['current']['creator_user_id'], 'Unkown Sales Agent'),
            'status': body['current'].get('status'),
            'from_stage': body['previous']['stage_id'],
            'to_stage': body['current']['stage_id'],
            'title': body['current']['title'],
        }
        message = rendered_template("pipeline_update.html", context=payload)
        color = "green"
        self.say(message, html=True, color=color)
        self.say("(boom)", color=color)

        return 'OK'

    @periodic(hour='1', minute='0', day_of_week="mon-fri")
    def update_pipedrive_users(self):
        """Update the cached list of Pipedrive users (user_id) periodically."""
        pipedrive_users = {}
        self.save('pipedrive_users', pipedrive_users)
