;; Add whatever commands you want to execute at the beginning
(print "Nextcloud")

;; Change the URL here
(setv base_url "https://path.to.my.nextcloud/")

;; Save into variables the "username" and "password" arguments of the
;; User object type defined with `(setv users (Users [{...}{...}] ))`
;; later in this project.
(setv username (Variable "username"))
(setv password (Variable "password"))

;; Saves the oc_sessionPassphrase cookie into the session_id variable.
(setv session_id (Cookie "oc_sessionPassphrase"))

;; Saves the first cookie whose name matches the regex (the cookie's
;; name is instance specific, better to use regex than the exact name).
(setv csrf_token (Cookie.regex "^[a-z0-9]{12}$"))

;; Other cookies used by nextcloud.
(setv nc_token (Cookie "nc_token"))
(setv nc_session_id (Cookie "nc_session_id"))
(setv nc_username (Cookie "nc_username"))

;; Extract the request_token using Regex plugin.
(setv request_token
      (Regex
        :name "request_token"
        ;; Everything after the first double quote (") in the
        ;; `data-requesttoken="` until but excluding the next double
        ;; quote (that's where the token ends).
        :regex "data-requesttoken=\"([^\"]+)\""))

;; Create the Users object. Use the following format:
;; (setv users
;;       (Users
;;         [{"username" "password"}
;;          {"user2" "password2" :optional "whatever"}
;;          {"user3" "password3"}]))
(setv users
      (Users
        [{"admin"
          "AdminPassword"}
         {"bot"
          "BotPassword"}]))
