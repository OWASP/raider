;; Add whatever commands you want to execute at the beginning
(print "Mastodon")

;; Change the URL here
(setv base_url "https://url.to.mastodon.instance")

;; Save into variables the "username" and "password" arguments of the
;; User object type defined with `(setv users (Users [{...}{...}] ))`
;; later in this project.
(setv username (Variable "username"))
(setv password (Variable "password"))
;; Sets `mfa_code` as a Prompt Plugin, which will ask for the MFA code
;; in the terminal.
(setv mfa_code (Prompt "MFA"))

;; Extracts the CSRF token using Html plugin. In this case it looks
;; for the first plugin that resembles:
;; <meta name="csrf-token" content="[A-Za-z0-9-_]+$">
;; and it'll extract the content attribute.
(setv csrf_token
      (Html
        :name "csrf_token"
        :tag "meta"
        :attributes
        {:content "^[A-Za-z0-9-_]+$"
	 :name "csrf-token"}
        :extract "content"))

;; Save the cookies used by mastodon
(setv session_id (Cookie "_session_id"))
(setv remember_user (Cookie "remember_user_token"))
(setv mastodon_session (Cookie "_mastodon_session"))


;; Create the Users object. Use the following format:
;; (setv users
;;       (Users
;;         [{"username" "password"}
;;          {"user2" "password2" :optional "whatever"}
;;          {"user3" "password3"}]))
(setv users
      (Users
        [{"admin"
          "password"
          :nickname "admin"}
         {"user1" "password1" :test "blah"}]))
