More details to come...

You must create a text file called `secrets/front_end.yaml` that contains a password that you wish to use for encrypting cookies, as well as Google authentication tokens. Below is an example. Details to come...

```
cookie: "abcdefg"
google_oauth_key: "111111111111-vsig111a11aa11aaaa1aaaaa1aaaa1aa.apps.googleusercontent.com"
google_oauth_secret: "A11AAAAaAAAAaAAAaa1aAAaa"
```

Also in the secrets directory:

MARIADB_ROOT_PASSWORD - This will be the root password. Use whatever password you would like to use.
MARIADB_USER - This will be the user ID that the app will use to access the database.
MARIADB_PASSWORD - This will be the password that the app will use to access the database.
MARIADB_DATABASE - The name of the database.
