# Prompt Library

## Prompt 1 — Generate a complete teaching kit
You are a careful peer-teaching assistant. Create a 10-minute lesson kit about **[TOPIC]** for **[LEVEL]** learners in **[LANGUAGE]**. Include: simple explanation, three common misconceptions and corrections, four timed lesson steps, exactly six slides with concise bullets, a one-page handout, five multiple-choice questions with four options and an answer key, and a checklist of claims that must be verified. Do not invent citations. Return valid structured JSON.

## Prompt 2 — Simplify an explanation
Explain **[TOPIC]** to a beginner in simple language. Use one everyday analogy, one accurate technical example, and a short summary. Mention where the analogy has limitations. Do not invent facts or sources.

## Prompt 3 — Check for misconceptions
List common misunderstandings about **[TOPIC]**. For each, provide a correction and a brief reason. Mark claims that require checking against a course textbook or reliable reference.

## Prompt 4 — Build an exit quiz
Write five multiple-choice questions about **[TOPIC]** for **[LEVEL]** learners. Use four options per question, one best answer, and a short explanation. Avoid ambiguous questions.

## Prompt 5 — Review the AI draft
Review this draft for factual errors, unsupported claims, unclear wording, outdated details, and misleading analogies: **[PASTE DRAFT]**. Identify each issue and suggest a correction. Do not claim external verification unless a source was actually checked.

## Prompt 6 — Improve after classroom testing
Here is anonymized learner feedback and quiz data: **[PASTE DATA]**. Suggest changes to the explanation, example, activity, and quiz. Do not infer more than the data supports.

### Prompt evaluation log
| Prompt version | Topic tested | What worked | What failed | Change made |
|---|---|---|---|---|
| v1 | [Topic] | [Observed result] | [Observed result] | [Edit] |
