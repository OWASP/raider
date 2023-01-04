(setv base_url "http://localhost:3000")

(setv question
      (Json
        :name "question"
        :extract "data[0]"))

(setv email (Variable "username"))
(setv password (Variable "password"))
(setv answer (Variable "answer"))
(setv authtoken
      (Json
        :name "authtoken"
        :extract "authentication.token"))

(setv user_id
      (Json
        :name "user_id"
        :extract "data.id"))

(setv authcookie
      (Cookie.from_plugin authtoken "token"))

(setv username_field
      (Regex
        :name "username_field"
        :regex "(<p style=\"margin-top:8%; color: #FFFFFF; text-align: center;\">.*</p>)<form action=\"./profile/image/file\""))


(setv users
      (Users
        [{"username@mail.com" "password"
          :answer "Security answer"}]))
