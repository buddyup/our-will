import boto

from will import settings
from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
from mixins import ServersMixin, GithubMixin, Stack

class StagingPlugin(WillPlugin, ServersMixin, GithubMixin):
    
    @require_settings("GITHUB_USERNAME","GITHUB_PASSWORD","GITHUB_ORGANIZATION_NAME",)
    @respond_to("(?:refresh|update) (?:repo|branch|github) info")
    def refresh_all_info(self, message):
        """update github info: refreshes the github branches and deploy.ymls"""
        self.say("Sure. One minute...", message=message)
        self.refresh_all_cached_github_info()
        self.say("All github branch and repo info refreshed.", message=message)

    @respond_to("(?:what branches are available for staging\?|(?:list|show) deployable branches)")
    def available_branches(self, message):
        """list deployable branches: list all the branches that can be deployed"""
        print "available_branches"
        repos = self.get_github_deployable_repos()
        context = {"repos": repos}
        branches_html = rendered_template("available_branches.html", context)
        self.say(branches_html, message=message, html=True)

    @respond_to("(?:^what branches do we have open\?|^(?:list|show) (?:all )?branches)")
    def all_branches(self, message):
        """list all branches: list all branches on repos you can see"""
        repos = self.get_github_all_repos()
        context = {"repos": repos}
        branches_html = rendered_template("available_branches.html", context)
        self.say(branches_html, message=message, html=True)
    
    @respond_to("(?:^what (?:staging )?stacks (?:do we have|are there)\?|^list stacks|^stacks|^staged)")
    def list_stacks(self, message):
        """list stacks: list all staging stacks"""
        context = {"stacks": self.stacks}
        branches_html = rendered_template("active_staging_stacks.html", context)
        self.say(branches_html, message=message, html=True)
    
    @require_settings("DEPLOY_PREFIX", "PUBLIC_URL", "HEROKU_API_KEY", 
        "HEROKU_EMAIL", "SSH", "SSH_PUB", )
    @respond_to("^(stage|(?:new |create a?)(?:staging )?stack for) (?P<branch_name>.*)")
    def create_stack(self, message, branch_name=None):
        """new stack for ____: create a new staging stack for branch ____"""
        if not branch_name:
            self.say("You didn't say which branch to stage.", message=message)

        self.say("Making a new stack for %s..." % branch_name, message=message) 
        branch = self.get_branch_from_branch_name(branch_name, is_deployable=True)
        if not branch:
            self.say("Can't find a branch named %s" % branch_name, message=message, color="red")
        elif type(branch) is type([]):
            branches_text = "\n- ".join(["%s/%s" % (b.repo_name, b.name) for b in branch])
            self.say("Found multiple matches.\n - %s" % branches_text, message=message, color="red")
        else:
            stack = self.new_stack(branch)
            self.say("Stack %s created and initialized." % (stack.name, ), message=message)
            self.say("Deploying... <a href='%s'>View log</a>" % (stack.deploy_log_url, ), message=message, html=True)
            if self.load(stack.active_deploy_key, False):
                self.say("%s is already deploying!" % (stack.name,), message=message)
            else:
                self.deploy(stack)
                self.save(stack.active_deploy_key, False)
                self.say("@%s %s deployed on stack %s. %s" % (message.sender.nick, branch.name, stack.name, stack.url, ), message=message)
            
    @require_settings("DEPLOY_PREFIX", "PUBLIC_URL", "HEROKU_API_KEY", 
        "HEROKU_EMAIL", "SSH", "SSH_PUB", )
    @respond_to("^new (school called|instance) (?P<school_name>.*)")
    def new_instance(self, message, school_name=None):
        """new school called ____: create a new instance for a school named ____"""
        if not school_name:
            self.say("You didn't tell me the name of the school.", message=message)
        else:

            self.say("Making a new BuddyUp instance for %s..." % school_name, message=message) 
            branch = self.get_branch_from_branch_name("buddyup/master", is_deployable=True)

            stack_name = school_name
            stack = Stack(branch=branch, name=stack_name)

            if "buddyup-%s" % stack_name in [s.name for s in stack.adapter.heroku.apps]:
                self.say("http://%s.buddyup.org already exists - I won't overwrite it." % (stack.name,), message=message)
            else:
                if self.load(stack.active_deploy_key, False):
                    self.say("%s is already being created." % (stack.name,), message=message)
                else:
                    self.say("Creating %s instance... <a href='%s'>View log</a>" % (stack.name, stack.deploy_log_url, ), message=message, html=True)
                    
                    # Make the s3 bucket.
                    AWS_name = "buddyup-%s" % stack.name
                    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
                    try:
                        bucket = conn.get_bucket(AWS_name)
                    except boto.exception.S3ResponseError:
                        bucket = conn.create_bucket(AWS_name)
                    except:
                        import traceback; traceback.print_exc();
                    
                    self.deploy(stack)
                    instance_url = "%s.buddyup.org" % stack.name

                    # Set the config.
                    stack.adapter.app.config["DEMO_SITE"] = "false"
                    stack.adapter.app.config["DOMAIN_NAME"] = instance_url
                    stack.adapter.app.config["AUTH0_CALLBACK_URL"] = "http://%s/callback" % instance_url
                    stack.adapter.app.config["AWS_S3_BUCKET"]  = AWS_name
                    stack.adapter.app.config["INTERCOM_APP_ID"] = "5714bb0i"
                    stack.adapter.app.config["SSO_INSTANCE"] = "true"

                    # Set the domain.
                    stack.adapter.run_heroku_cli_command("domains:add %s" % instance_url)
                    
                    # Reset the DB.
                    stack.adapter.run_heroku_cli_command("run scripts/reset --app %s" % AWS_name)

                    self.save(stack.active_deploy_key, False)

                    self.say("@%s %s is available at http://%s." % (message.sender.nick, stack.name, instance_url, ), message=message)
                    self.say("@steven if this is a permanent school, make sure to add it to circle.yml and uptime.py.", message=message)


    @require_settings("DEPLOY_PREFIX", "PUBLIC_URL", "HEROKU_API_KEY", 
        "HEROKU_EMAIL", "SSH", "SSH_PUB", )
    @respond_to("^reset hudson")
    def reset_hudson(self, message):
        """new school called ____: create a new instance for a school named ____"""
        self.say("You got it.  Give me one minute...", message=message)
        stack = Stack(branch="master", name="hudson")
        stack.adapter.run_heroku_cli_command("run python scripts/reload-demo-database.py --app=hudson-buddyup")
        self.say("@%s hudson's been reset!" % (message.sender.nick,), message=message)

    @respond_to("^(?P<force>force )?redeploy (?P<code_only>code to )?(?P<branch_or_stack_name>.*)")
    def redeploy(self, message, force=False, code_only=False, branch_or_stack_name=None):
        """redeploy ____: redeploy the stack named ____"""
        if code_only is not False:
            code_only = True
        if not branch_or_stack_name:
            self.say("You didn't say which branch or stack to redeploy.", message=message)
        if force is not False:
            force = True

        do_deploy = False
        stack = None
        self.say("Redeploying %s..." % branch_or_stack_name, message=message)
        branch = self.get_branch_from_branch_name(branch_or_stack_name, is_deployable=True)
        if not branch:
            stack = self.get_stack_from_stack_name(branch_or_stack_name)
            if not stack:
                self.say("Can't find a branch or stack named %s" % branch_or_stack_name, message=message, color="red")

            if stack:
                branch = stack.branch
                do_deploy = True

        elif type(branch) is type([]):
            branches_text = "\n-%s".join(branch)
            self.say("Found multiple matches. %s" % branches_text, message=message)
        elif branch:
            stack = self.get_stack_from_branch_name(branch_or_stack_name)
            if not stack:
                self.say("We don't have a deployed stack of %s.  To create one, say \"make a new stack for %s\"" %
                    (branch_or_stack_name, branch_or_stack_name)
                , color="red")
            elif type(stack) is type([]):
                stacks_text = "\n-%s".join(stack)
                self.say("Found multiple matches. %s" % stacks_text, message=message, color="red")
            else:
                do_deploy = True
        
        if do_deploy:
            if self.load(stack.active_deploy_key, False) and not force:
                self.say("%s is already deploying!" % (stack.name,), message=message)
            else:
                self.say("Branch and stack found. Deploying... <a href='%s'>View log</a>" % (stack.deploy_log_url, ), message=message, html=True)
                self.deploy(stack, code_only=code_only, force=force)
                self.save(stack.active_deploy_key, False)
                self.say("@%s Redeployed %s on %s. %s" % (message.sender.nick, branch.name, stack.name, stack.url), message=message)

    
    @respond_to("^(destroy stack|unstage|tear ?down) (?P<stack_name>.*)")
    def destroy_staging(self, message, stack_name=None):
        """unstage ____: tear down the stack named ____"""
        if not stack_name:
            self.say("You didn't say which stack to destroy.", message=message)
        else:
            stack = self.get_stack_from_stack_name(stack_name)
            if not stack:
                self.say("Couldn't find a stack named %s." % stack_name, message=message)
            else:
                self.say("Destroying %s..." % stack_name, message=message)
                self.destroy_stack(stack)
                self.save(stack.active_deploy_key, False)
                self.say("@%s Stack %s has been destroyed." % (message.sender.nick, stack_name), message=message)
    
    @periodic(hour='17', minute='0', second='0', day_of_week="mon-fri")
    def remind_staging_servers(self):
        context = {
            "stacks": self.stacks,
            "no_stacks": self.stacks == {}
        }
        servers_html = rendered_template("active_staging_server_reminder.html", context)
        color = "green"
        if self.stacks != {}:
            color = "red"
            self.say(servers_html, html=True, color=color)

    @periodic(hour='18', minute='0', second='0', day_of_week="mon-fri")
    def seriously_remind_staging_servers(self):
        if self.stacks != {}:
            context = {
                "stacks": self.stacks,
                "no_stacks": self.stacks == {}
            }
            servers_html = rendered_template("active_staging_server_reminder.html", context)
            self.say(servers_html, html=True, color="red")


    @route("/deploy-log/<stack_name>")
    @rendered_template("deploy_log.html")
    def show_deploy_log(self, stack_name):
        stack = self.get_stack_from_stack_name(stack_name)
        deploy_output = None
        if stack:
            deploy_output = self.load(stack.deploy_output_key)
        return {
            "stack": stack,
            "stack_name": stack_name,
            "deploy_output":deploy_output,
            "output_update_url": "/deploy-log/output/%s" % stack_name,
        }

    @route("/deploy-log/output/<stack_name>")
    def deploy_output(self, stack_name):
        stack = self.get_stack_from_stack_name(stack_name)
        if stack:
            key = stack.deploy_output_key
        else:
            key = "deploy_output_%s" % stack_name.lower().replace(" ", "_")
        try:
            deploy_output = self.load(key)
            return deploy_output
        except:
            return "Error loading output"


    @route("/deploy-log/")
    @rendered_template("stacks.html")
    def stack_list_page(self):
        stacks = self.stacks.values()
        return {"stacks": stacks}

    @route("/stacks/")
    @rendered_template("stacks.html")
    def stack_list_page(self):
        stacks = self.stacks.values()
        return {"stacks": stacks}

