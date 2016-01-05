import random
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from will import settings

VALUES = [
    "Radical Authenticity. Be who we are, fully, with honesty, transparency, and passion.",
    "Do the Right Thing. Ethically and personally, do the right thing for each other, our users, and the world.",
    "Build Real Relationships. Intentionally focus on building and strengthening genuine relationships between students, clients, and each other.",
    "Listen. Use Active Listening. Seek feedback. Listen fully before talking.",
    "Communicate Clearly and Often. Spend the effort to communicate well, in writing and speech.  Communicate more often than you think is necessary. Never say sorry.",
    "Use Science. Hypothesize, Experiment, Measure, Learn.",
    "Invest in Tools. Turn knowledge and processes into people-independent tools.",
    "Work Where, When and How You're at Your Best. Find the spot where you’re at your best, and make the most of it.  Bring your best self and best hours to BuddyUp.",
    "Seek Discomfort. Continually and intentionally put yourself in situations where you'll grow.",
    "Get Shit Done. Be a proactive, no-ego doer.",
]


class MonthlyGoalsPlugin(WillPlugin):

    @respond_to("Set (?:the )?monthly goals to (?P<goals>.*)", multiline=True)
    def set_goals(self, message, goals=""):
        """set the monthly goals to ___: Set our monthly goals."""
        print "goals: %s" % goals
        self.save("monthly_goals", goals)
        self.say("Got it.", message=message)

    @periodic(hour='13', minute='0', day_of_week="sun")
    def say_goals_on_monday(self):
        self.say_goals()

    @respond_to("^(?:What are the )?(?:monthly )?goals")
    def respond_to_goals_question(self, message):
        """what are the monthly goals?: Posts the monthly goals."""
        self.say_goals(message=message)

    def say_goals(self, message=None):
        goals = self.load("monthly_goals", False)
        if goals:
            self.say("@all our monthly goals:\n %s" % goals, message=message, html=True)
        else:
            self.say("No monthly goals set.", message=message)

    @periodic(hour='10', minute='0', day_of_week="mon-fri")
    def say_value(self):
        self.say("@here here's a value to focus on today: %s" % random.choice(VALUES))
