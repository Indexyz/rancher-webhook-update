from . import rancher
import threading
import telegram
import time

class DeployThread(threading.Thread):
    def __init__(self, rancher, service, config, message=None):
        self.rancher = rancher
        self.service = service
        self.config = config
        self.message = message
        if config.ENABLE_TELEGRAM:
            self._telegram_bot = telegram.Bot(token=config.TELEGRAM_BOT_TOKEN)

        super(DeployThread, self).__init__()
    
    def sendTelegramMessage(self, message):
        if self.config.ENABLE_TELEGRAM:
            self._telegram_bot.send_message(chat_id=self.config.TELEGRAM_CHAT_ID, text=message)

    def run(self):
        if self.message:
            self.sendTelegramMessage("""A new commit has been pushed and CI passed.
Project: {}
Commit Id: {}
Commit By: {} <{}>
Commit Message: 
{}

Rancher agent will automatically redeploy to include the changes.
""".format(
        self.message['project']['path_with_namespace'], 
        self.message['commit']['id'][:16], 
        self.message['commit']['author']['name'],
        self.message['commit']['author']['email'],
        self.message['commit']['message'].strip())
    )
        
        while self.rancher.getServiceState(self.service) != rancher.STATE_ACTIVE:
            print "Some task is deploying, sleeping."
            time.sleep(1)

        self.rancher.upgradeService(self.service)
        while self.rancher.getServiceState(self.service) != rancher.STATE_UPGRADED:
            time.sleep(1)
            print "Cheacking status error, sleeping."

        self.rancher.finishServiceUpgrade(self.service)

        if self.message:
            self.sendTelegramMessage("""Redeployed.
Commit Id: {}

Changes have been applied to rancher.
""".format(self.message['commit']['id'][:16]))

        print "Finished deploy, theading down!"