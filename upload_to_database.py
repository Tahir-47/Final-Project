import streamlit_authenticator as stauth

import postgreData as db

usernames = ["tahir", "nihalR","nihalJ","dilu" ]
names = ["Tahir Mohammed", "Nihal Rajeev", "Nihal Jasim", "Muhammed Dilu"]
passwords = ["1234", "1234", "1234", "1234"]
hashed_passwords = stauth.Hasher(passwords).generate()


for (username, name, hash_password) in zip(usernames, names, hashed_passwords):
    db.insert_user(username, name, hash_password)