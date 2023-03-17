dataset = {
    "d0:14:11:b0:11:c8": [
        {
            "cmd": "switch-on",
            "type": 0,
            "description": "0",
            "endpoint": 1,
            "check-rules": [],
            "actions": [
                {
                    "cmd": "switch-on",
                    "mac-addr": "d0:14:11:b0:11:c8",
                    "endpoint": 4,
                    "level": 255,
                    "duration": 50,
                    "timeout-ms": 1000
                },
                {
                    "cmd": "switch-on",
                    "mac-addr": "d0:14:11:b0:11:c8",
                    "endpoint": 5,
                    "level": 255,
                    "duration": 50,
                    "timeout-ms": 1000
                },
                {
                    "cmd": "switch-on",
                    "mac-addr": "d0:14:11:b0:11:c8",
                    "endpoint": 6,
                    "level": 255,
                    "duration": 50,
                    "timeout-ms": 1000
                }
            ]
        },
        {
            "cmd": "switch-off",
            "type": 0,
            "description": "0",
            "endpoint": 1,
            "check-rules": [],
            "actions": [
                {
                    "cmd": "switch-on",
                    "mac-addr": "d0:14:11:b0:11:c8",
                    "endpoint": 8,
                    "level": 255,
                    "duration": 50,
                    "timeout-ms": 1000
                }
            ]
        }
    ]
}



channel_number = 1
target_channels = list()

data = dataset.get("d0:14:11:b0:11:c8")
for i in data:
    if i["endpoint"] == channel_number:
        target_actions = i["actions"]
        for target in target_actions:
            target_channels.append((target["endpoint"], target["mac-addr"]))

print(channel_number)
print(target_channels)