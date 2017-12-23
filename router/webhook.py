from flask import make_response
from rancher import rancher
from rancher import deploy
from rancher import service
from flask import request
import time

def attach(app):
    @app.route('/webhook')
    def webhook():
        config = app.i_config
        if not (request.headers.get("x-auth-token") == config.WEBHOOK_PASS):
            resp = make_response("Auth Token Error", 401)
            return resp

        # Make rancher great again!
        rancher_service = service.Service(
            config.RANCHER_PROJECT_ID, config.RANCHER_SERVICE_ID
        )
        rancher_instance = rancher.Rancher(
            config.RANCHER_HOST, config.RANCHER_ACCESS_KEY, config.RANCHER_SCRECT_KEY
        )
        deploy.DeployThread(rancher_instance, rancher_service).start()

        return "Deploy theading started"