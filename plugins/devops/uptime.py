import requests
import time

from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings

class UptimePlugin(WillPlugin):

    def _verify_url(self, url):
        try:
            r = requests.get(url)
            if not r.status_code == 200:
                time.sleep(5)
                r = requests.get(url)
                if not r.status_code == 200:
                    self.say("@all WARNING: %s is down! (%s code)" % (url, r.status_code), color="red")

                    on_fire_list = self.load("on_fire_list", [])
                    self.send_email(
                        from_email="ERROR <errors@buddyup.org>",
                        email_list=on_fire_list,
                        subject="Website %s error - %s" % (r.status_code, url),
                        message="%s is down!" % url
                    )
        except:
            pass

    @periodic(second='5')
    def buddyup_is_up(self):
        self._verify_url("http://www.buddyup.org")

    @periodic(second='5')
    def pdx_is_up(self):
        self._verify_url("http://pdx.buddyup.org")

    @periodic(second='5')
    def ecampus_oregonstate_is_up(self):
        self._verify_url("http://ecampus.oregonstate.buddyup.org")

    @periodic(second='5')
    def oit_is_up(self):
        self._verify_url("http://oit.buddyup.org")

    @periodic(second='5')
    def oregonstate_is_up(self):
        self._verify_url("http://oregonstate.buddyup.org")

    @periodic(second='5')
    def hudson_is_up(self):
        self._verify_url("http://hudson.buddyup.org")

    @periodic(second='5')
    def stanford_is_up(self):
        self._verify_url("http://stanford.buddyup.org")

    @periodic(second='5')
    def stanford_is_up(self):
        self._verify_url("http://canadacollege.buddyup.org")

    @periodic(second='5')
    def stanford_is_up(self):
        self._verify_url("http://skylinecollege.buddyup.org")

    @periodic(second='5')
    def stanford_is_up(self):
        self._verify_url("http://collegeofsanmateo.buddyup.org")

    @periodic(second='5')
    def buddyup_dashboard_is_up(self):
        self._verify_url("https://buddyup-dashboard.herokuapp.com")

    @respond_to("^add (?P<email>.*) to the on fire list", multiline=True)
    def add_to_fire_list(self, message, email=""):
        on_fire_list = self.load("on_fire_list", [])
        on_fire_list.append(email)

        self.save("on_fire_list", on_fire_list)
        self.say("Got it, added %s to the on fire list" % email, message=message)

    @respond_to("^on fire list", multiline=True)
    def get_fire_list(self, message):
        on_fire_list = self.load("on_fire_list", [])
        fire_list_html = rendered_template("fire_list.html", {"fire_list": on_fire_list})
        self.say(fire_list_html, message=message, html=True)

    @respond_to("^remove (?P<email>.*) from the on fire list", multiline=True)
    def remove_from_fire_list(self, message, email=""):
        on_fire_list = self.load("on_fire_list", [])
        on_fire_list.remove(email)

        self.save("on_fire_list", on_fire_list)
        self.say("Got it, removed %s from the on fire list" % email, message=message)

    @respond_to("^send test email to the on fire list", multiline=True)
    def test_on_fire_emails(self, message):
        on_fire_list = self.load("on_fire_list", [])

        self.send_email(
            from_email="TEST ERROR <errors@buddyup.org>",
            email_list=on_fire_list,
            subject="Test Website 500 error -- just kidding!",
            message="Everything is fine :)"
        )

        self.say("Sent out the test email", message=message)
