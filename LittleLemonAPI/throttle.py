from rest_framework.throttling import UserRateThrottle

class PerMinuteThrottle(UserRateThrottle):
    scope='one'