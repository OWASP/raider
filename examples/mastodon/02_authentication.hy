;; Defines the first AuthFlow object (A Flow that affects
;; authentication). In this case it's the `initialization` Flow.
(setv initialization
      (AuthFlow
        :request (Request
                   ;; Sends a GET request.
                   :method "GET"
                   ;; To https://ghost.server.url/about.
                   :url (Combine base_url "/about"))
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
                       (NextStage "login")
                       :otherwise
                       ;; Quit with an error if no
                       (Error "Cannot initialize session"))]))

;; Defines the second AuthFlow object called `login`.
(setv login
      (AuthFlow
        :request
        (Request
          ;; Sends a POST request
          :method "POST"
          ;; To https://ghost.server.url/auth/sign_in.
          :url (Combine base_url "/auth/sign_in")
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
                       (NextStage "multi_factor"))
                     (Http
                       ;; If no MFA user is authenticated
                       :status 302
                       :action
                       (Print "Authentication successful"))]))


;; Defines the last AuthFlow object for MFA.
(setv multi_factor
      (AuthFlow
        :request
        (Request
          ;; Sends a POST request
          :method "POST"
          ;; To https://ghost.server.url/auth/sign_in.
          :url (Combine base_url "/auth/sign_in")
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
                     (NextStage "multi_factor")
                     :otherwise
                     (Print "Authenticated successfully"))]))
