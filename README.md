# trivio

**Trivio** is django-based application that was designed for building yet another simple (i.e. _trivial_) social network.

## Features:
  * JWT authentication;
  * email verification through `hunter.io` on signup;
  * profile enrichment based on `clearbit.com/enrichment`;
  * API:
    * user creation and login;
    * post creation & retrieve;
    * post listing;
    * post like;
    * post unlike;
For the sake of simplicity friendship is not implemented yet. So it's social network for introverts!

## Notes
  * IMO, it's better to make async enrichment of the user data
  (i.e. to do it after user creation in the separate celery task), but nevertheless it's task-specific
  and for the sake of simplicity I'm doing sync call;
  * sqlite3 is enough to implement the API and can be easily replaced with more 'production' database;
  * API is very limited, but it's enough to implement the bot.

## Proof-of-Concept bot
  TODO