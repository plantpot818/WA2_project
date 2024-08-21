# Exam planner / finder 
## Inspiration
This idea was derived off my original plan of making a exam seats planner system for teachers to use, however that was dropped because of the fluctuations in seats among different venues (classrooms, seminar rooms, lecture halls, etc) and it would be quite niche if it was designed only for places like the hall. So then I decided to condense it into simpler program of being able to set up exam plans and push them onto a website for students to see.

## How it's built
It is built using basic flask functions, sqlite3, uuid for the token system as well as basic html and css.

## Challenges encountered
Mountains of them were encountered, I had lots of trouble with using sqlite3 within my python app before my awesome computing teacher brushed us up on the language and allowed me to understand how to commit changes and properly format sqlite3 commands within the app. The file upload system was also troublesome to deal with as it was something new to me and I was not very familar with the os module that was suggested to me by an AI. Datetime functions were also a bit difficult to grasp but I eventually got them down to validate my dates and time related inputs.

## Accomplishments that I'm proud of
Actually connecting my db for once and learning how to use a new interpreter (vscode). Creating a working token system with expiry dates

## What I learned
How to create a token system for admin sites, how to set up a file upload, many sqlite3 functions

## What's next for Exam planner / finder
I definitely need to add a way to modify existing exam plans and maybe validate the subjects input too. After that I might revisit the original seats idea and incorporate it into the app.
