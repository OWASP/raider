(setv users
      (Users
        [{"multi@authenticationtest.com" "pa$$w0rd"}]))

(setv username (Variable "username"))
(setv password (Variable "password"))

(setv session_id
      (Cookie "PHPSESSID"))


(setv initialize_session
      (Flow
        (Request.get "https://authenticationtest.com/multiStepAuth/")
        :operations [(Next "send_login")]
        :outputs [session_id]))

(setv send_login
      (Flow
        (Request.post "https://authenticationtest.com/multiStepAuth/?step=2"
          :cookies [session_id]
          :data {"email" username})
        :operations [(Print.headers)
                     (Next "send_password")]))


(setv send_password
      (Flow
        (Request.post "https://authenticationtest.com/login/?mode=multiChallenge"
          :cookies [session_id]
          :data {"email" username
                 "password" password})
        :operations [(Print.headers ["Location"])]))
