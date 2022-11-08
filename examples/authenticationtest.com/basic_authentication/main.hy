(setv users
      (Users
        [{"user" "pass"}]))

(setv username (Variable "username"))
(setv password (Variable "password"))


(setv complex_form_auth
      (Flow
        
        (Request
          :url "https://authenticationtest.com/HTTPAuth/"
          :method "GET"
          :headers [(Header.basicauth "user" "pass")])
        :operations [(Print.headers ["Location"])]))
