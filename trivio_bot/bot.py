#!/usr/bin/env python3
import yaml
import argparse
import logging
import random
import string
import requests


class JwtAuth:
    def __init__(self, username, api_url, auth_suffix, auth_credentials, refresh_suffix):
        self._username = username
        self._access_token = None
        self._refresh_token = None
        self._api_url = api_url
        self._auth_url = api_url + auth_suffix
        self._auth_credentials = auth_credentials
        self._refresh_url = api_url + refresh_suffix

    def login(self):
        logging.info(f"logging in for user {self._username}")
        response = requests.post(self._auth_url, json=self._auth_credentials)
        if response.status_code != 200:
            raise RuntimeError(f"can't login for user {self._username}")
        data = response.json()
        self.set_auth(data["access"], data["refresh"])

    def update_access_token(self):
        assert self._refresh_token is not None
        response = requests.post(self._refresh_url, json={
            "refresh": self._refresh_token
        })
        if response.status_code == 401:
            self.login()
            return
        if response.status_code != 200:
            raise RuntimeError(f"can't refresh token for {self._username}")
        data = response.json()
        new_refresh = data.get("refresh") or self._refresh_token
        self.set_auth(data["access"], new_refresh)

    def set_auth(self, access, refresh):
        self._access_token = access
        self._refresh_token = refresh

    def get(self, url, json, **kwargs):
        return self._request(1, 'get', url, json, **kwargs)

    def _request(self, attempts, method, url, json=None, **kwargs):
        headers = dict(kwargs.pop('headers', {}))
        no_auth = kwargs.pop("no_auth", False)
        if not no_auth:
            if not self._access_token:
                self.login()
            headers['Authorization'] = f'Bearer {self._access_token}'
        response = requests.request(method, self._api_url + url, json=json, headers=headers, **kwargs)
        if not no_auth and response.status_code == 401:
            if attempts <= 0:
                raise RuntimeError("Server keep saying HTTP 401 though there was successful login")
            self.update_access_token()
            return self._request(attempts - 1, method, url, json, headers=headers, **kwargs)
        return response

    def post(self, url, json=None, **kwargs):
        return self._request(1, 'post', url, json, **kwargs)


def ensure_response_ok(response):
    if not (200 <= response.status_code < 300):
        raise RuntimeError(f"bad response for {response.url}: {response.status_code} {response.json()}")


class Post:
    def __init__(self, id, user, title):
        self.id = id
        self.title = title
        self.num_likes = 0
        self.user = user

    def like_by(self, user):
        response = user.jwt_auth.post(f"/posts/{self.id}/like/")
        ensure_response_ok(response)
        self.num_likes += 1
        user.num_likes += 1


class User:
    def __init__(self, username, jwt: JwtAuth, target_num_posts, target_num_likes):
        self.id = None
        self.username = username
        self.posts = []
        self.target_num_posts = target_num_posts
        self.target_num_likes = target_num_likes
        self.num_likes = 0
        self.jwt_auth = jwt

    def login(self):
        self.jwt_auth.login()

    def create_post(self, title, content):
        response = self.jwt_auth.post("/posts/", {
            "content": content,
            "title": title
        })
        ensure_response_ok(response)
        return Post(response.json()["id"], self, title)

    def signup(self, username, email, password):
        response = self.jwt_auth.post("/auth/signup/", {
            "username": username,
            "email": email,
            "password": password
        }, no_auth=True)
        if response.status_code == 201:
            data = response.json()
            self.id = data["id"]
            self.jwt_auth.set_auth(data["access"], data["refresh"])
            return True
        return False


def main(config):
    users = []
    posts = []
    logging.info("creating users")
    while len(users) < config["number_of_users"]:
        # some creativity about mails
        first_name = random.choice(config["first_names"])
        last_name = random.choice(config["last_names"])
        birthday = random.randint(70, 99)
        username = f"{first_name}.{last_name}"
        if birthday >= 80:
            username += str(birthday)
        email = f"{username}@gmail.com"
        password = "".join(random.choices(string.digits + string.ascii_letters, k=16))
        jwt = JwtAuth(
            username,
            config["base_url"] + "/api/v1",
            "/auth/login/",
            {"username": username, "password": password},
            "/auth/refresh/",
        )
        user = User(
            username,
            jwt,
            target_num_posts=random.randint(0, config["max_posts_per_user"]),
            target_num_likes=random.randint(0, config["max_likes_per_user"]),
        )
        logging.info(f"trying user {username}")
        if user.signup(username, email, password):
            logging.info(f"created user {user.username}")
            users.append(user)
    logging.info("creating posts")
    for user in users:
        for i in range(user.target_num_posts - len(user.posts)):
            mood = random.choice(config["moods"])
            post = user.create_post(f"Current mood: {mood}", f"{mood}")
            posts.append(post)
            logging.info(f"user {user.username} created post {post.id} with title '{post.title}'")

    logging.info("making likes")
    users.sort(key=lambda u: -len(u.posts))
    for user in users:
        liked_posts = set()
        while user.num_likes < user.target_num_likes:
            non_liked_posts = [p for p in posts if p.num_likes == 0]
            if not non_liked_posts:
                break
            likeable_users = set(p.user.id for p in non_liked_posts if user.id != p.user.id)
            likeable_posts = [p for p in posts if p.user.id in likeable_users and p.id not in liked_posts]
            if not likeable_posts:
                logging.info(f"no more posts to like for user {user.username}")
                break
            post = random.choice(likeable_posts)
            post.like_by(user=user)
            liked_posts.add(post.id)
            logging.info(f"user {user.username} liked post {post.id}, like {user.num_likes}/{user.target_num_likes}")
    logging.info("done")


if __name__ == "__main__":
    logging.basicConfig(format='{asctime} {levelname} [{module}] {message}', style='{', level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parsed_args = parser.parse_args()
    with open(parsed_args.config) as f:
        cfg = yaml.safe_load(f)
    main(cfg)
