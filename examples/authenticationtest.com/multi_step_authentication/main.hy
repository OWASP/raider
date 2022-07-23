(setv users
      (Users
        [{"multi@authenticationtest.com" "pa$$w0rd"}]))

(setv username (Variable "username"))
(setv password (Variable "password"))

(setv session_id
      (Cookie "PHPSESSID"))


(setv initialize_session
      (AuthFlow
        :request
        (Request
          :url "https://authenticationtest.com/multiStepAuth/"
          :method "GET")
        :operations [(NextStage "send_login")]
        :outputs [session_id]))


(setv send_login
      (AuthFlow
        :request
        (Request
          :url "https://authenticationtest.com/multiStepAuth/?step=2"
          :method "POST"
          :cookies [session_id]
          :data {"email" username})
        :operations [(Print.headers)
                     (NextStage "send_password")]))


(setv send_password
      (AuthFlow
        :request
        (Request
          :url "https://authenticationtest.com/login/?mode=multiChallenge"
          :method "POST"
          :cookies [session_id]
          :data {"email" username
                 "password" password})
        :operations [(Print.headers ["Location"])]))
