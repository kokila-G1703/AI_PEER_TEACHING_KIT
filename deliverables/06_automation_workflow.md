# Automation / Workflow

## Prototype workflow
1. Student enters a topic, level and preferred language.
2. Flask validates the topic and sends a prompt to the Groq API.
3. The AI returns structured teaching content.
4. Flask validates that the response contains six slides and five quiz questions.
5. The result page displays the lesson kit and quiz.
6. Student submits the quiz.
7. Flask calculates the score and saves the attempt in SQLite.
8. The progress page displays saved attempts.
9. Presenter manually verifies selected claims and records corrections in the verification report.

## Optional no-code extension
Use Google Forms to collect anonymous pre-test and post-test responses. A spreadsheet can summarize scores. If using Zapier or another automation service, document the trigger, action, sample data and consent/privacy decisions.

## What is automated?
Content drafting, basic output checks, quiz scoring and local score storage.

## What is not automated?
Independent fact verification, classroom teaching, confirming student identity, and deciding whether the lesson was educationally effective.
