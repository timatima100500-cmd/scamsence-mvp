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



PS C:\\Windows\\System32> **Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"

Swag Examples**
1. {

&#x20; "content": "Congratulations! You won $1,000,000. Send your SSN to claim.",

&#x20; "content\_type": "text"

}

2. {

&#x20; "content": "http://youtube.com/post/UgkxKENMGThqyHR9kKb7UTHksw5T4kdgFqvb?si=k968t0dTT-JiLYGy",

&#x20; "content\_type": "link"

}

3. Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/analyze" `

&#x20; -Method POST -ContentType "application/json" `

&#x20; -Body '{"content": "URGENT: Your account suspended! Send bitcoin now or lose everything!", "content\_type": "text"}'


4. Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/analyze" `

&#x20; -Method POST -ContentType "application/json" `

&#x20; -Body '{"content": "Most people treat the 9-to-5 like gravity, as if it is just how work works. It is not. The idea of reporting to a fixed employer at fixed hours for a fixed wage is about 100 years old at scale, essentially one century out of all of human history.

Before the Industrial Revolution, few people had jobs. They had work. Craftspeople worked when work needed doing. Farmers worked by season, harvest, and task. Artisans owned their skills, output, and hours. Work was tied to what got made, not to how many hours you sat somewhere.



The Factory

Factories needed coordination. Machines needed workers on the same schedule. Henry Ford adopted the five-day, 40-hour workweek at his company in 1926. The Fair Labor Standards Act made it federal law in 1938.



We have been operating inside that 1938 framework ever since.



The 9-to-5 was never designed for you. It was designed for the factory. The fact that knowledge workers, creatives, and consultants are still operating inside a structure built for assembly lines is one of the great unexamined absurdities of modern life.



What AI Actually Changes

A huge barrier was the cost of doing business. Working independently used to mean hiring a team. You needed an editor, a designer, a marketer, an accountant, and someone to handle customer service, plus the capital to pay all of them. For most people, this was not a viable path.



Now, AI brings cost down to almost nothing. One person with good judgment, taste, lived experience, expertise, and the right AI tools can now do what used to take a team of five, and that changes the real economics of working for yourself. This is the return of the artisan, this time with leverage. An Intentional Start

Most -use AI to escape your job- articles stop here. They give you the vision, a framework, five prompts, and a pep talk. Then the hard questions start.

How do I actually get a client?

How do I actually sell something?

How do I keep delivering when I am doing this alone?

This is the part that rarely gets covered.

The Messy Middle

The business you are building has three problems to solve, in order:



Finding the people who need what you know



Closing them, turning interest into a yes and a payment



Delivering and making it repeatable



A strong prompt can handle any one of these. An agent skill handles it the same way every time, without rebuilding the prompt from scratch on every new client.



An agent skill is a packaged set of instructions, plus any templates or scripts it needs, that your AI tool loads on its own when the task calls for it. Build it once, and the tool reuses it across every conversation, turning a general assistant into a specialist at one job.



Officially, an -agent skill- is -a standardized way to give AI agents new capabilities and expertise",

"content\_type": "text"
}'


5\. 

5.1 
$body = @{

&#x20;   content = @"

Вставь сюда

любой длинный текст

с переносами строк

"@

&#x20;   content\_type = "text"

} | ConvertTo-Json



5.2
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/analyze" `

&#x20; -Method POST -ContentType "application/json" `

&#x20; -Body $body







6\. $body = @{

&#x20;   content = @"

Most people treat the 9-to-5 like gravity, as if it is just how work works. It is not. The idea of reporting to a fixed employer at fixed hours for a fixed wage is about 100 years old at scale, essentially one century out of all of human history.

Before the Industrial Revolution, few people had jobs. They had work. Craftspeople worked when work needed doing. Farmers worked by season, harvest, and task. Artisans owned their skills, output, and hours. Work was tied to what got made, not to how many hours you sat somewhere.



The Factory

Factories needed coordination. Machines needed workers on the same schedule. Henry Ford adopted the five-day, 40-hour workweek at his company in 1926. The Fair Labor Standards Act made it federal law in 1938.



We have been operating inside that 1938 framework ever since.



The 9-to-5 was never designed for you. It was designed for the factory. The fact that knowledge workers, creatives, and consultants are still operating inside a structure built for assembly lines is one of the great unexamined absurdities of modern life.



What AI Actually Changes

A huge barrier was the cost of doing business. Working independently used to mean hiring a team. You needed an editor, a designer, a marketer, an accountant, and someone to handle customer service, plus the capital to pay all of them. For most people, this was not a viable path.



Now, AI brings cost down to almost nothing. One person with good judgment, taste, lived experience, expertise, and the right AI tools can now do what used to take a team of five, and that changes the real economics of working for yourself. This is the return of the artisan, this time with leverage. An Intentional Start

Most -use AI to escape your job- articles stop here. They give you the vision, a framework, five prompts, and a pep talk. Then the hard questions start.

How do I actually get a client?

How do I actually sell something?

How do I keep delivering when I am doing this alone?

This is the part that rarely gets covered.

The Messy Middle

The business you are building has three problems to solve, in order:



Finding the people who need what you know



Closing them, turning interest into a yes and a payment



Delivering and making it repeatable



A strong prompt can handle any one of these. An agent skill handles it the same way every time, without rebuilding the prompt from scratch on every new client.



An agent skill is a packaged set of instructions, plus any templates or scripts it needs, that your AI tool loads on its own when the task calls for it. Build it once, and the tool reuses it across every conversation, turning a general assistant into a specialist at one job.



Officially, an -agent skill- is -a standardized way to give AI agents new capabilities and expertise

"@

&#x20;   content\_type = "text"

} | ConvertTo-Json









































































