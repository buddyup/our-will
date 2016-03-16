"""Pipedrive CRM Plugin for Will.

Requries settings.PIPEDRIVE_KEY which can be set in the OS enviroment as WILL_PIPEDRIVE_KEY
"""

import requests
from will.plugin import WillPlugin
from will.decorators import (
    periodic,
    rendered_template,
    route,
)
from will import settings


class PipedrivePlugin(WillPlugin):
    """A Will plugin for BuddyUp's CRM Pipedrive's webhooks."""

    def _raise_for_missing_pipedrive_key(self):
        """Raise an AttributeError if PIPEDRIVE_KEY is missing from settings."""
        if not hasattr(settings, 'PIPEDRIVE_KEY'):
            raise AttributeError('PIPEDRIVE_KEY missing from settings, please set WILL_PIPEDRIVE_KEY in the env.')

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
        assert self.request.json and "current" in self.request.json and "previous" in self.request.json
        pipedrive_users = self.pipedrive_users
        stages = self.pipedrive_stages
        print "\n\n\n Stages: ", stages, "\n\n\n"
        body = self.request.json

        user = pipedrive_users.get(body['current']['creator_user_id'])
        if not user:
            self.update_pipedrive_users()
            user = pipedrive_users.get(body['current']['creator_user_id'], {})

        payload = {
            'name': user.get('name', 'Unknown Sales Agent'),
            'from_stage': body['previous']['stage_id'],
            'to_stage': body['current']['stage_id'],
            'title': body['current']['title'],
        }

        if self._pipedrive_deal_stage_changed(body):
            message = rendered_template("pipedrive_update.html", context=payload)
            self.say(message, html=True, color="green")

        if self._pipedrive_deal_status_lost(body):
            message = rendered_template("pipedrive_lost.html", context=payload)
            self.say(message, html=True, color="red")

        if self._pipedrive_deal_status_won(body):
            message = rendered_template("pipedrive_won.html", context=payload)
            self.say(message, html=True, color="green")

        return 'OK'

    @periodic(hour='1', minute='0', day_of_week="mon-fri")
    def update_pipedrive_users(self):
        """Update the cached list of Pipedrive users (user_id) periodically."""
        self._raise_for_missing_pipedrive_key()
        url = 'https://api.pipedrive.com/v1/users'
        resp = requests.get(url, params={'api_token': settings.PIPEDRIVE_KEY})
        payload = resp.json()
        pipedrive_users = {
            user['id']: user for user in payload['data']
        }
        self.save('pipedrive_users', pipedrive_users)
        self._pipedrive_users = pipedrive_users

    def _fetch_stages_for_pipeline(self, pipeline_id):
        url = 'https://api.pipedrive.com/v1/stages'
        resp = requests.get(url, params={'api_token': settings.PIPEDRIVE_KEY, 'pipeline_id': pipeline_id})
        payload = resp.json()
        return payload['data']

    @periodic(hour='1', minute='10', day_of_week="mon-fri")
    def update_pipedrive_stages(self):
        """Get pipedrive stages from storgage or API."""
        self._raise_for_missing_pipedrive_key()
        pipeline_ids = self.pipedrive_pipelines.keys()
        pipedrive_stages = {
            stage['id']: stage
            for p_id in pipeline_ids
            for stage in self._fetch_stages_for_pipeline(p_id)
        }
        self.save('pipedrive_stages', pipedrive_stages)
        self._pipdrive_stages = pipedrive_stages

    def update_pipedrive_pipelines(self):
        """Get pipedrive pipelines from storgage or API."""
        self._raise_for_missing_pipedrive_key()
        url = 'https://api.pipedrive.com/v1/pipelines'
        resp = requests.get(url, params={'api_token': settings.PIPEDRIVE_KEY})
        payload = resp.json()
        pipedrive_pipelines = {
            pipeline['id']: pipeline for pipeline in payload['data']
        }
        self.save('pipedrive_pipelines', pipedrive_pipelines)
        self._pipedrive_pipelines = pipedrive_pipelines

    @property
    def pipedrive_users(self):
        """Pipedrive sales agents/users."""
        if not hasattr(self, "_pipedrive_users"):
            self._pipedrive_users = self.load('pipedrive_users')
            if not self._pipedrive_users:
                self.update_pipedrive_users()

        return self._pipedrive_users

    @property
    def pipedrive_stages(self):
        """Pipedrive stages."""
        if not hasattr(self, "_pipedrive_stages"):
            self._pipedrive_stages = self.load('pipedrive_stages')
            if not self._pipedrive_stages:
                self.update_pipedrive_stages()

        return self._pipedrive_stages

    @property
    def pipedrive_pipelines(self):
        """Pipedrive pipelines."""
        if not hasattr(self, "_pipedrive_pipelines"):
            self._pipedrive_pipelines = self.load('pipedrive_pipelines')
            if not self._pipedrive_pipelines:
                self.update_pipedrive_pipelines()

        return self._pipedrive_pipelines
