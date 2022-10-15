(setv users
      (Users
        [{"xsrf@authenticationtest.com" "pa$$w0rd"}]))

(setv username (Variable "username"))
(setv password (Variable "password"))

(setv session_id
      (Cookie "PHPSESSID"))

(setv csrf_token
      (Html
        :name "csrf_token"
        :tag "input"
        :attributes {:name "xsrfToken"
                     :id "xsrfToken"}
        :extract "value"))

(setv initialize_session
      (Flow
        :request
        (Request
          :url "https://authenticationtest.com/xsrfChallenge/"
          :method "GET")
        :operations [(Print csrf_token)
                     (NextStage "login")]
        :outputs [csrf_token
                  session_id]))

(setv login
      (Flow
        :request
        (Request
          :url "https://authenticationtest.com/login/?mode=xsrfChallenge"
          :method "POST"
          :cookies [session_id]
          :data {"email" username
                 "password" password
                 "xsrfToken" csrf_token})
        :operations [(Print.headers ["Location"])]))
