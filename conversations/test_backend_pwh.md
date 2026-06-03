**Bold: Commands**



PowerShell 7.6.2

PS C:\\Windows\\System32> **Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/analyze" `**

**>>   -Method POST -ContentType "application/json" `**

**>>   -Body '{"content": "Can we meet at 3pm tomorrow?", "content\_type": "text"}'**



verdict          : Legitimate

probability      : 0

red\_flags        : {}

explanation      : No significant fraud indicators found. Message appears legitimate.

recommendations  : {Stay vigilant — even trusted channels can be compromised.}

model\_used       : mock-analyzer-v2

analysis\_time\_ms : 0



PS C:\\Windows\\System32> **Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/analyze" `**

**>>   -Method POST -ContentType "application/json" `**

**>>   -Body '{"content": "URGENT: Your account suspended! to unlock it Send 10USD now or lose everything!", "content\_type": "text"}'**



verdict          : Likely Scam

probability      : 60

red\_flags        : {@{pattern=urgency; description=Urgency keyword; severity=7}, @{pattern=urgency; description=Account

&#x20;                  suspension threat; severity=9}}

explanation      : Multiple suspicious signals found. Verify the sender before taking any action.

recommendations  : {Check the sender via the official website or phone number., Do not act under time pressure — scammers

&#x20;                  create false urgency., Call the organization directly using a number from their official site.}

model\_used       : mock-analyzer-v2

analysis\_time\_ms : 16

similar\_cases    : {}



PS C:\\Windows\\System32> **Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"**



