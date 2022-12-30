(setv login_sqli
      (Flow
        (Request.post
          (with-baseurl "rest/user/login")
          :json
          {"email" (Prompt "Email payload")
           "password" "password"})
        :outputs [authtoken]
        :operations
        [(Print.body)
         (Http
           :status 200
           :action
           (Success "Logged in successfully")
           :otherwise
           (Next "login_sqli"))]))

(setv sqli_test
      (FlowGraph login_sqli))
