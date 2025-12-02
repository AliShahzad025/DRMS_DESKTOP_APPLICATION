class AlertService:

    def __init__(self, repo):
        self.repo = repo

    def create_alert(self, message, severity, location):
        return self.repo.create(message, severity, location)

    def get_alert(self, alert_id):
        return self.repo.get_by_id(alert_id)

    def list_alerts(self):
        return self.repo.get_all()

    def update_alert(self, alert_id, **data):
        return self.repo.update(alert_id, **data)

    def delete_alert(self, alert_id):
        return self.repo.delete(alert_id)
