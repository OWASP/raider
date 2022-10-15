(setv users
      (Users
        [{"delay@authenticationtest.com" "pa$$w0rd"}]))

(setv username (Variable "username"))
(setv password (Variable "password"))


(setv simple_form_auth
      (Flow
        :request
        (Request
          :url "https://authenticationtest.com/login/?mode=delayChallenge"
          :method "POST"
          :data {"email" username
                 "password" password})
        :operations [(Print.headers ["Location"])]))
