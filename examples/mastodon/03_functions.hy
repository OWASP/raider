;; Extract the mastodon nickname from HTML. It'll look for a tag
;; similar to:
;; <input id="account_display_name" data-default="my_nickname">
;; and extract the value in the `data-default` attribute.
(setv nickname
      (Html
        :name "nickname"
        :tag "input"
        :attributes
        {:id "account_display_name"}
        :extract "data-default"))

;; Go to user's profile to extract the nickname.
(setv get_nickname
      (Flow
         (Request.get
           (Combine base_url "/settings/profile")
           :cookies [mastodon_session session_id remember_user])
        :outputs [nickname]
        :operations [(Print nickname)]))
