(setv users
      (Users
        [{"bootstrap@authenticationtest.com" "pa$$w0rd"}]))

(setv username (Variable "username"))
(setv password (Variable "password"))

(setv session_id
      (Cookie "PHPSESSID"))

(setv captcha
      (Html
        :name "captcha"
        :tag "code"
        :attributes {}
        :extract "contents"))

(setv get_captcha
      (Flow
        :request
        (Request
          :url "https://authenticationtest.com/bootstrapAuth/"
          :method "GET")
        :operations [(Print captcha)
                     (NextStage "interactive_auth")]
        :outputs [captcha
                  session_id]))

(setv interactive_auth
      (Flow
        :request
        (Request
          :url "https://authenticationtest.com/login/?mode=bootstrapAuth"
          :method "POST"
          :cookies [session_id]
          :data {"email" username
                 "password" password
                 "captcha" captcha})
        :operations [(Print.headers ["Location"])]))
