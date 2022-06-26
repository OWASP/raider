;; Extracts the username using a Regex
(setv nickname
      (Regex
        :name "nickname"
        :regex "href=\"/user/([^\"]+)"))

;; Gets the nickname from main page
(setv get_nickname
      (Flow
        :request (Request
                   :method "GET"
                   :cookies [session_id reddit_session]
                   :url base_url)
        :outputs [nickname]
        :operations [(Print nickname)]))


;; Gets unread messages
(setv get_unread_messages
      (Flow
        :request (Request
                   :method "GET"
                   ;; Use the access_token as a Bearer HTTP
                   ;; Authorization header.
                   :headers [(Header.bearerauth access_token)
                             (Header "User-Agent" "Mozilla 5.0")]
                   :url "https://s.reddit.com/api/v1/sendbird/unread_message_count")
        :operations [(Print.body)]))
