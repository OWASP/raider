(setv users
      (Users
        [{"complex@authenticationtest.com" "pa$$w0rd"}]))

(setv username (Variable "username"))
(setv password (Variable "password"))


(setv complex_form_auth
      (Flow
        (Request.post
          "https://authenticationtest.com/login/?mode=complexAuth"
          :data {"email" username
                 "password" password
                 "selectLogin" "yes"
                 "loveForm" "on"})
        :operations [(Print.headers ["Location"])]))
