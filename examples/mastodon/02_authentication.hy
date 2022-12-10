;; Defines the first Flow object (A Flow that affects
;; authentication). In this case it's the `initialization` Flow.
(setv initialization
      (Flow
        (Request.get
          ;; Sends a GET request.
          ;; To https://ghost.server.url/about.
          (Combine base_url "/about"))
        ;; Extract the csrf_token using Html and mastodon_session using
        ;; Cookie objects.
        :outputs [csrf_token mastodon_session]
        :operations [
                     ;; Saves the response body to `/tmp/mastodon.html`
                     ;; Comment out for debugging.
                     ;; (Save.body "/tmp/mastodon.html")

                     ;; Print the extracted csrf_token and mastodon_session
                     (Print csrf_token mastodon_session)
                     ;; Check if the HTTP response status was 200 OK.
                     (Http
                       :status 200
                       :action
                       ;; Go to `login` stage if yes
                       (Next "login")
                       :otherwise
                       ;; Quit with an error if no
                       (Error "Cannot initialize session"))]))

;; Defines the second Flow object called `login`.
(setv login
      (Flow
        (Request.post
          ;; Sends a POST request
          ;; To https://ghost.server.url/auth/sign_in.
          (Combine base_url "/auth/sign_in")
          ;; Only `mastodon_session` cookie is needed.
          :cookies [mastodon_session]
          ;; Sends the csrf_token together with the username and
          ;; password in the POST body.
          :data
          {"authenticity_token" csrf_token
           "user[email]" username
           "user[password]" password})
        :outputs [mastodon_session ;; Server sends an updated mastodon_session
                  session_id ;; session_id is needed from this step forwards
                  remember_user ;; cookie used for "remember user" functionality
                  csrf_token] ;; new CSRF token
        :operations [(Grep
                       :regex "Invalid Email or password"
                       :action
                       ;; Quits if invalid credentials.
                       (Error "Invalid credentials"))
                     (Grep
                       ;; Goes to the next stage if MFA is enabled.
                       :regex "Enter the two-factor code"
                       :action
                       (Next "multi_factor"))
                     (Http
                       ;; If no MFA user is authenticated
                       :status 302
                       :action
                       (Print "Authentication successful"))]))


;; Defines the last Flow object for MFA.
(setv multi_factor
      (Flow
        (Request.popst
          ;; Sends a POST request
          ;; To https://ghost.server.url/auth/sign_in.
          (Combine base_url "/auth/sign_in")
          ;; Using three cookies
          :cookies [mastodon_session
                    session_id
                    remember_user]
          ;; Add updated CSRF token and the prompted MFA code in the
          ;; POST body.
	  :data
          {"authenticity_token" csrf_token
           "user[otp_attempt]" mfa_code})
        ;; Extract new CSRF token, updated cookies
        :outputs [csrf_token mastodon_session session_id remember_user]
        :operations [(Grep
                     ;; Repeat the stage if MFA failed
                     :regex "Invalid two-factor code"
                     :action
                     (Next "multi_factor")
                     :otherwise
                     (Print "Authenticated successfully"))]))
