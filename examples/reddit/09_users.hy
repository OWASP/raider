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
