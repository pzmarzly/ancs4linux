"""ANCS revision 2014-10-20"""

ANCS_SERVICE = "7905f431-b5ce-4e99-a40f-4b1e122d00d0"
NOTIFICATION_SOURCE_CHAR = "9fbf120d-6301-42d9-8c58-25e699a21dbd"
CONTROL_POINT_CHAR = "69d1d8f3-45e1-49a8-9821-9bbdfdaad9d9"
DATA_SOURCE_CHAR = "22eac6e9-24d6-4bb5-be44-b36ace7c7bfb"
ANCS_CHARS = [NOTIFICATION_SOURCE_CHAR, CONTROL_POINT_CHAR, DATA_SOURCE_CHAR]


class CategoryID(int):
    Other = 0
    IncomingCall = 1
    MissedCall = 2
    Voicemail = 3
    Social = 4
    Schedule = 5
    Email = 6
    News = 7
    HealthAndFitness = 8
    BusinessAndFinance = 9
    Location = 10
    Entertainment = 11


class EventID(int):
    NotificationAdded = 0
    NotificationModified = 1
    NotificationRemoved = 2


class EventFlag(int):
    Silent = 1 << 0
    Important = 1 << 1
    PreExisting = 1 << 2
    PositiveAction = 1 << 3
    NegativeAction = 1 << 4


class CommandID(int):
    GetNotificationAttributes = 0
    GetAppAttributes = 1
    PerformNotificationAction = 2


class NotificationAttributeID(int):
    AppIdentifier = 0
    Title = 1
    Subtitle = 2
    Message = 3
    MessageSize = 4
    Date = 5
    PositiveActionLabel = 6
    NegativeActionLabel = 7


class ActionID(int):
    Positive = 0
    Negative = 1


class AppAttributeID(int):
    DisplayName = 0
