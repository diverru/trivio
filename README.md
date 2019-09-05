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
Bot config is yaml file, where you can specify such parameters as:
  * `first_names`, `last_names`, `moods` - for name/text generations;
  * `base_url` - api backend base url;
  * `number_of_users` - number of users to create;
  * `max_posts_per_user` - max number of posts to create per user;
  * `max_likes_per_user` - max number of likes to perform per user;
  
Bot performs following activity:
  1. signup `number_of_users` users;
  2. create random number of posts (but at most `max_posts_per_user`) for each user;
  3. after signups and posting, performs liking activity:
      1. take user with maximum number of posts that made no more than `max_likes_per_user` likes
      2. take random post from other user that have at least one non-liked post;
      3. like it
      4. if there are no posts to like or `max_likes_per_user` reached, take next user at the step 1
      
Notes:
  * for real-world bot we need to make more features for bot:
    - random delays between actions to avoid bans;
    - more meaningful post content;
    - retries for requests to deal with network and availability problems;
    - save/retrieve bot current state;
    - probably some async/parallel code for interaction with API;
  * probably, we need to make more API for retrieving current backend state, such as posts/users retrieve for given filters;
    but I have no enough time now to write them.
