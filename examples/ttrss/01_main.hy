(setv base_url "https://path.to.ttrss.server/")

;; Extract CSRF token using a Regex.
(setv csrf_token
      (Regex
        :name "csrf_token"
        :regex "const __csrf_token = \"([^\"]+)\""))

;; Save credentials in variables.
(setv username (Variable "username"))
(setv password (Variable "password"))

;; Session Cookie used by TTRSS.
(setv ttrss_sid (Cookie "ttrss_sid"))

;; Prompt for the MFA code if enabled.
(setv mfa_code (Prompt "MFA"))

;; First Login Flow
(setv login
      (Flow
        (Request.post
          :url (Combine base_url "/public.php")
          :data
          ;; Sends credentials.
          {"op" "login"
           "login" username
           "password" password
           "profile" 0}
          )
        ;; Gets the session cookie.
        :outputs
        [ttrss_sid]
        :operations
        [(Http
           :status 200 ;; ttrss responds with 200 when MFA is enabled
           :action
           [(Print "Multi-factor authentication is enabled.")
            (Next "multi_factor")]
           :otherwise
           [(Print "Multi-factor authentication is disabled.")
            (Next "main_page")])]))

;; Runs MFA request, sending the MFA code prompted from the user, and
;; goes to main page upon finishing.
(setv multi_factor
      (Flow
        (Request.post
          (with-baseurl "/public.php")
          :data
          {"op" "login"
           "login" username
           "password" password
           "bw_limit" ""
           "safe_mode" ""
           "remember_me" ""
           "profile" 0
           "otp" mfa_code})
        :outputs [ttrss_sid]
        :operations [(Next "main_page")]))

;; Go to main page to see if user is authenticated.  Flow type since
;; it doesn't affect the authentication state.
(setv main_page
      (Flow
        (Request.get (Combine base_url "/")
          :cookies [ttrss_sid])
        :outputs [csrf_token]
        :operations [(Grep
                       :regex "Incorrect username or password"
                       :action (Print "Login failed")
                       :otherwise (Print "Login succeeded"))]))

;; Define request that'll return the list of feeds.
(setv get_feeds
      (Flow
        (Request.post
          (Combine base_url "/backend.php")
          :cookies [ttrss_sid]
          :data
          {"op" "feeds"
           "method" "view"
           "feed" -4  ;; -4 ~ All articles
           "view_mode" "adaptive"
           "order_by" "default"
           "cat" "false"
           "csrf_token" csrf_token})
        :operations
        [(Print.body)])) ;; Print the JSON body with the list of feeds

;; Another Flow to oget the list of labels
(setv get_labels
      (Flow
        (Request.get
          (Combine base_url "/backend.php")
          :cookies [ttrss_sid]
          :data
          {"op" "pref-labels"
           "method" "getlabeltree"})
        :operations
        [(Print.body)])) ;; Print the JSON body with the list of labels
