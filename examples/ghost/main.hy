;; Add whatever commands you want to execute at the beginning
(print "Ghost")

;; Change the URL here
(setv base_url "https://ghost.server.url/")

;; Save into variables the "username" and "password" arguments of the
;; User object type defined with `(setv users (Users [{...}{...}] ))`
;; later in this project.
(setv username (Variable "username"))
(setv password (Variable "password"))

;; Saves the `ghost-admin-api-session` cookie into the `session_id`
;; variable.
(setv session_id
      (Cookie "ghost-admin-api-session"))


;; Defines the first/only Flow object (A Flow that affects
;; authentication). In this case it's the `login` Flow.
(setv login
      (Flow
         (Request.post
           ;; Sends a POST request.
           ;; To this path, built by combining the base URL
           ;; with the absolute path.
           (Combine base_url "/ghost/api/v3/admin/session")
           ;; Only username and password needed in POST body
           :data
           {"password" password
            "username" username})
         ;; Extracts the output from `session_id` (Cookie) to be used
         ;; in further requests.
         :outputs [session_id]
         ;; If server responds with HTTP 404, it means the login
         ;; failed, so Raider quits with an error message.
         :operations [(Http
                        :status 404
                        :action (Error "Login failed"))]))


;; Defines a new Flow object to get the user's information. Doesn't
;; affect authentication therefore it's created as a Flow object and
;; not an Flow one.
(setv get_user_info
      (Flow
         (Request.get
           ;; Sends a GET request.
           ;; To this path, built by combining the base URL
           ;; with the absolute path.
           (Combine base_url "/ghost/api/canary/admin/users/me/")
           ;; Using the `session_id` cookie we got from the
           ;; `login` Flow.
           :cookies [session_id]
           ;; Data to include in the GET query
           :data {"include" "roles"})
         ;; Just print the response body.
         :operations [(Print.body)]))

;; Defines a new Flow object to get the existing tags.
(setv get_tags
      (Flow
         (Request.get
           (Combine base_url "/ghost/api/v3/admin/tags/?limit=all")
           :cookies [session_id])
        :operations [(Print.body)]))

;; Defines a new Flow object to get the existing posts.
(setv get_posts
      (Flow
         (Request.get
           (Combine base_url "/ghost/api/canary/admin/posts/")
           :cookies [session_id])
         :operations [(Print.body)]))
