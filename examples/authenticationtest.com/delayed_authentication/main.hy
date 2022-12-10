(setv users
      (Users
        [{"delay@authenticationtest.com" "pa$$w0rd"}]))

(setv username (Variable "username"))
(setv password (Variable "password"))


(setv simple_form_auth
      (Flow
        (Request.post
          "https://authenticationtest.com/login/?mode=delayChallenge"
          :data {"email" username
                 "password" password})
        :operations [(Print.headers ["Location"])]))
