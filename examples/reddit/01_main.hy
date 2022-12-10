(print "Reddit")
(setv base_url "https://www.reddit.com/")

;; Create a new custom plugin to open pass
;; (https://www.passwordstore.org/) and read the one-time-password
;; (OTP) for reddit MFA. This is optional, you can comment it out and
;; use Prompt manually to introduce the MFA code.
(defclass PasswordStore [Plugin]
  ;; initialize PasswordStore as (PasswordStore "name" "path")
  (defn __init__ [self name path]
    (setv self.path path)
    ;; init the Plugin with run_command as its function.
    (.__init__ (super)
               :name name
               :function (. self run_command)))
  (defn run_command [self]
    (import os)
    ;; Runs `pass otp path/to/password/entry` and reads its value
    (setv self.value
          ((.strip
             ((.read
                (os.popen
                  (+ "pass otp " self.path)))))))
    (return self.value)))



;; Only inputs
(setv username (Variable "username"))
(setv password (Variable "password"))
;; (setv mfa_code (Prompt "MFA"))
(setv mfa_code (PasswordStore
                 :name "otp"
                 :path "personal/reddit"))


;; Read CSRF Token from Html tags. Looks for:
;; <input name="csrf_token" value="^[0-9a-f]{40}$" type="hidden".
;; Extracts the `value` attribute.
(setv csrf_token
      (Html
        :name "csrf_token"
        :tag "input"
        :attributes
        {:name "csrf_token"
         :value "^[0-9a-f]{40}$"
         :type "hidden"}
        :extract "value"))

;; Gets the access_token using Regex Plugin.  Looks at the string
;; between the next double quotes enclosed in round brackets ().
(setv access_token
      (Regex
        :name "access_token"
        :regex "\"accessToken\":\"([^\"]+)\""))

;; Saves the session cookies
(setv session_id (Cookie "session"))
(setv reddit_session (Cookie "reddit_session"))
