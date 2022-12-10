(setv users
      (Users
        [{"user" "pass"}]))

(setv username (Variable "username"))
(setv password (Variable "password"))


(setv complex_form_auth
      (Flow
        (Request.get "https://authenticationtest.com/HTTPAuth/"
          :headers [(Header.basicauth "user" "pass")])
        :operations [(Print.headers ["Location"])]))
