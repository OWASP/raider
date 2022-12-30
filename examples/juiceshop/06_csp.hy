(setv get_csp_header
      (Flow
        (Request.get
          (with-baseurl "profile")
          :cookies [authcookie])
        :operations [(Print.headers ["Content-Security-Policy"])
                     (Match
                       (Prompt "Satisfied with the result? y/n") "y"
                       :action (Success "CSP set up")
                       :otherwise (Next "change_picture_url"))]))

(setv change_picture_url
      (Flow
        (Request.post
          (with-baseurl "profile/image/url")
          :cookies [authcookie]
          :data
          {"imageUrl" (Prompt "image URL")})
        :operations [(Print "Waiting for server to time out (30 seconds)")
                     '(import time)
                     '(.sleep time 30)
                     (Next "get_csp_header")]))



(setv csp_test
      (FlowGraph
        get_csp_header))
