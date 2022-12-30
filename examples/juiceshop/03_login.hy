(setv login
      (Flow
        (Request.post
          (with-baseurl "rest/user/login")
          :json
          {"email" email
           "password" password})
        :outputs [authtoken]
        :operations
        [(Http
           :status 401
           :action (Failure "Login failed")
           :otherwise [(Print authtoken)
                       (Success "Login successfull")])]))


