(setv users
      (Users
        [{"simpleForm@authenticationtest.com" "pa$$w0rd"}]))
      
(setv username (Variable "username"))
(setv password (Variable "password"))
      

(setv simple_form_auth
      (AuthFlow
        :request
        (Request
          :url "https://authenticationtest.com/login/?mode=simpleFormAuth"
          :method "POST"
          :data {"email" username
                 "password" password})
        :operations [(Print.headers ["Location"])]))
          
