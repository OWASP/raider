;; Defines the first Flow object (A Flow that affects
;; authentication). In this case it's the `initialization` Flow.
(setv initialization
      (Flow
         (Request.get
           (Combine base_url "/login"))
         ;; Just gets the initial tokens from the server needed to start
         ;; login.
         :outputs [session_id csrf_token request_token]
         :operations [(Next "login")]))

;; Defines the last Flow object to actually log in.
(setv login
      (Flow
         (Request.post
           (Combine base_url "/login")
           ;; Sends some extra static cookies that nextcloud requires.
           :cookies [session_id
                     csrf_token
                     (Cookie "__Host-nc_sameSiteCookielax" "true")
                     (Cookie "__Host-nc_sameSiteCookiestrict" "true")]
           ;; Puts username, password and request_token in the
           ;; POST body.
           :data {"user" username
                  "password" password
                  "requesttoken" request_token})
         ;; Extracts nc_token and nc_session_id most
         ;; importantly. nc_username stores the username, and
         ;; csrf_token gets updated.
         :outputs [nc_token nc_session_id nc_username csrf_token]))
