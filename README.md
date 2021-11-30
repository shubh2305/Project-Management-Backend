Links for the api

1. users/get-access-token/
   POST => data = {
   token: string
   }
   Get a new access token. The token sent will be refresh token

2. users/verify-token/
   POST => data = {
   token: string
   }
   Verify if the token is still valid or not

3. users/register/
   POST => data = {
   email: string (required),
   password: string (required),
   first_name: string,
   last_name: string
   }
   Register a new user in the website

4. users/login/
   POST => data = {
   email: string (required),
   password: string (required)
   }
   Login user with the given email and password
