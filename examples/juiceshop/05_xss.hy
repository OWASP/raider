(setv get_user_profile
      (Flow
        (Request.get
          (with-baseurl "profile")
          :cookies [authcookie])
        :outputs [username_field]
        :operations [(Print username_field)
                     (Next "change_username")]))

(setv change_username
      (Flow
        (Request.post
          (with-baseurl "profile")
          :cookies [authcookie]
          :data
          {"username" (Prompt "new username")})
        :operations [(Next "get_user_profile")]))


(setv xss_test
      (FlowGraph
        get_user_profile))

