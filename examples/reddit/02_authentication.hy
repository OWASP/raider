;; Defines the first Flow object (A Flow that affects
;; authentication). In this case it's the `initialization` Flow.
(setv initialization
      (Flow
         (Request
                   :method "GET"
                   :url (Combine base_url "/login/"))
        ;; Extracts the CSRF token and the session id from reddit
        :outputs [csrf_token session_id]
        :operations [;; Prints the extracted tokens
                     (Print session_id csrf_token)
                     ;; But also show the three headers
                     (Print.headers ["Connection" "Pragma" "Server"])
                     ;; And print all returned cookies
                     (Print.cookies)
                     ;; Then goes to next stage
                     (NextStage "login")]))

;; Sends the login information here
(setv login
      (Flow
         (Request
                   :method "POST"
                   :url (Combine base_url "login")
                   :cookies [session_id]
                   ;; Sends user credentials and the csrf token in
                   ;; POST body.
                   :data
                   {"password" password
                    "username" username
                    "csrf_token" csrf_token
                    "otp" ""
                    "dest" base_url})
        ;; Updates session tokens
        :outputs [session_id reddit_session]
        :operations [(Print session_id reddit_session)
                     (Http
                       :status 200
                       :action
                       ;; if server responds with HTTP 200, run a Grep
                       ;; on the response for the string
                       ;; `TWO_FA_REQUIRED` to see whether MFA has
                       ;; been enabled.
                       (Grep
                         :regex "TWO_FA_REQUIRED"
                         :action
                         ;; If yes, print the message and go to next stage.
                         [(Print "Multi-factor authentication enabled")
                          (NextStage "multi_factor")]
                         ;; if no, login has succeeded, and it gets
                         ;; the access token next.
                         :otherwise
                         (NextStage "get_access_token"))
                       ;; if not HTTP 200 means login failed
                       :otherwise
                       (Error "Login error"))]))

;; If MFA is enabled, this Flow is needed.
(setv multi_factor
      (Flow
         (Request
                   :method "POST"
                   :url "https://www.reddit.com/login"
                   :cookies [session_id]
                   ;; Send same data, plus the otp code
                   :data
                   {"password" password
                    "username" username
                    "csrf_token" csrf_token
                    "otp" mfa_code
                    "dest" base_url})
        ;; Extracts the reddit_session token
        :outputs [reddit_session]
        :operations [(Print reddit_session csrf_token)
                     (Http
                       :status 200
                       :action
                       ;; If HTTP 200, goes get the access token.
                       (NextStage "get_access_token"))
                     (Http
                       :status 400
                       ;; if HTTP 400, run a Grep on response
                       :action
                       (Grep
                         ;; Print correct message and restart login
                         ;; process.
                         :regex "WRONG_OTP"
                         :action
                         [(Print "Wrong OTP")
                          (NextStage "initialization")]
                         :otherwise
                         [(Print "Bad CSRF")
                          (NextStage "initialization")]))]))


;; Gets the access_token needed for some actions on Reddit
(setv get_access_token
      (Flow
         (Request
                   :method "GET"
                   :url "https://www.reddit.com/"
                   :cookies [reddit_session])
        :outputs [access_token]
        :operations [(Print access_token)]))
