from rest_framework.throttling import UserRateThrottle


class TaskThrottle(UserRateThrottle):
    """
    Допълнителен throttle само за write методи към Task/Subtask.
    GET/HEAD/OPTIONS не се ограничават тук (важат само глобалните anon/user).
    """
    scope = "task-write"  # ще ползваме тази scope за write

    def allow_request(self, request, view):
        # за четене няма доп. ограничение
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # за write – прилагаме scope "task-write"
        self.scope = "task-write"
        self.rate = self.get_rate()
        if not self.rate:
            # ако няма дефиниран rate в settings, допускаме заявката
            return True
        self.num_requests, self.duration = self.parse_rate(self.rate)
        return super().allow_request(request, view)
