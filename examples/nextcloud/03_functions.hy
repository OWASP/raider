;; Gets a file from the nextcloud user's storage.
(setv get_file
      (Flow
        :request
        (Request
          :method "GET"
          ;; Prompt the user for the file path and gets its webdav url
          :url (Combine base_url "/remote.php/webdav/" (Prompt "Filepath:"))
          :cookies [session_id
                    csrf_token
                    (Cookie "__Host-nc_sameSiteCookielax" "true")
                    (Cookie "__Host-nc_sameSiteCookiestrict" "true")])
        ;; Prints the file contents on the terminal
        :operations [(Print.body)]))

;; Using nextcloud health (you need to install the app first on nextcloud).
;; First you need the request_token you get on the health app page.
(setv get_health_request_token
      (Flow
        :request
        (Request
          :method "GET"
          :url (Combine base_url "/apps/health/")
          :cookies [session_id
                    csrf_token
                    nc_session_id
                    nc_username
                    nc_token
                    (Cookie "__Host-nc_sameSiteCookielax" "true")
                    (Cookie "__Host-nc_sameSiteCookiestrict" "true")])
        :outputs [request_token]
        :operations [(NextStage "submit_weight")]))


;; For example if you want to submit the weight, you'd start by
;; testing with something like this:
(setv submit_weight
      (Flow
        :request
        (Request
          :method "POST"
          :url (Combine base_url "/apps/health/weight/dataset/person/1")
          ;; Add the request_tokens as a HTTP header (required for
          ;; request to work)
          :headers [(Header.from_plugin request_token "requesttoken")]
          :cookies [session_id
                    csrf_token
                    nc_session_id
                    nc_username
                    nc_token
                    (Cookie "__Host-nc_sameSiteCookielax" "true")
                    (Cookie "__Host-nc_sameSiteCookiestrict" "true")]
          :data
          (PostBody
            ;; Sends body as a Json encoded data
            :encoding "json"
            :data {"date" "2022-06-15"
                   "weight" "71.9"}))
        :operations [(Print.body)]))
