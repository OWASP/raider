(setv users
      (Users
        [{"dynamic@authenticationtest.com" "pa$$w0rd"}]))

(setv username (Variable "username"))
(setv password (Variable "password"))

(setv session_id
      (Cookie "PHPSESSID"))


(setv email_field
      (Html
        :name "email_field"
        :tag "input"
        :attributes {:type "email"}
        :extract "id"))

(setv password_field
      (Html
        :name "password_field"
        :tag "input"
        :attributes {:type "password"}
        :extract "id"))


(setv initialize_session
      (AuthFlow
        :request
        (Request
          :url "https://authenticationtest.com/dynamicChallenge/"
          :method "GET")
        :operations [(Print email_field password_field)
                     (NextStage "login")]
        :outputs [email_field
                  password_field
                  session_id]))

(setv login
      (AuthFlow
        :request
        (Request
          :url "https://authenticationtest.com/login/?mode=dynamicChallenge"
          :method "POST"
          :cookies [session_id]
          :data {email_field username
                 password_field password})
        :operations [(Print.headers ["Location"])]))
