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

    def _pipedrive_deal_status_lost(self, payload):
        return (
            payload['current']['status'] != payload['previous']['status'] and
            payload['current']['status'] == 'lost'
        )

    def _pipedrive_deal_status_won(self, payload):
        return (
            payload['current']['status'] != payload['previous']['status'] and
            payload['current']['status'] == 'won'
        )

    @route("/api/pipedrive-update", method="POST")
    def pipedrive_notification(self):
        """Web hook push notification endpoint from Pipedrive subscription(s) when a deal moves.

        https://developers.pipedrive.com/v1#methods-PushNotifications / REST Hooks / Web hooks
        """
        print self.request.json
        assert self.request.json and "current" in self.request.json and "previous" in self.request.json
        pipedrive_users = self.load('pipedrive_users') or {}
        body = self.request.json
        payload = {
            'name': pipedrive_users.get(body['current']['creator_user_id'], 'Unkown Sales Agent'),
            'from_stage': body['previous']['stage_id'],
            'to_stage': body['current']['stage_id'],
            'title': body['current']['title'],
        }

        if self._pipedrive_deal_stage_changed(body):
            message = rendered_template("pipedrive_update.html", context=payload)
            color = "green"
            self.say(message, html=True, color=color)

        if self._pipedrive_deal_status_lost(body):
            message = rendered_template("pipedrive_lost.html", context=payload)
            color = "red"
            self.say(message, html=True, color=color)

        if self._pipedrive_deal_status_won(body):
            message = rendered_template("pipedrive_won.html", context=payload)
            color = "green"
            self.say(message, html=True, color=color)

        return 'OK'

    @periodic(hour='1', minute='0', day_of_week="mon-fri")
    def update_pipedrive_users(self):
        """Update the cached list of Pipedrive users (user_id) periodically."""
        pipedrive_users = {}
        # TODO ALECK: Get these from the pipedrive API.
        self.save('pipedrive_users', pipedrive_users)

    @periodic(hour='1', minute='10', day_of_week="mon-fri")
    def update_pipedrive_stages(self):
        """Update the cached list of Pipedrive users (user_id) periodically."""
        pipedrive_stages = {}
        # TODO ALECK: Get these from the pipedrive API.
        self.save('pipedrive_stages', pipedrive_stages)
